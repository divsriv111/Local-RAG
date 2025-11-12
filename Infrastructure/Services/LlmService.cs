using System.Net.Http.Json;
using System.Runtime.CompilerServices;
using System.Text;
using System.Text.Json;
using Application.DTOs;
using Application.Interfaces;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;

namespace Infrastructure.Services;

public class LlmService : ILlmService
{
    private readonly HttpClient _httpClient;
    private readonly ILogger<LlmService> _logger;
    private readonly string _pythonServiceUrl;

    public LlmService(
        HttpClient httpClient,
        IConfiguration configuration,
        ILogger<LlmService> logger)
    {
        _httpClient = httpClient;
        _logger = logger;
        _pythonServiceUrl = configuration["PythonService:BaseUrl"] ?? "http://localhost:8000";
    }

    public async Task<LlmQueryResponseDto> QueryAsync(
        LlmQueryRequestDto request,
        CancellationToken cancellationToken = default)
    {
        try
        {
            _logger.LogInformation(
                "Sending LLM query for workspace {WorkspaceId}, chat {ChatHistoryId}, model {Model}",
                request.WorkspaceId, request.ChatHistoryId, request.LlmModel);

            var pythonRequest = MapToPythonRequest(request);
            var url = $"{_pythonServiceUrl}/api/llm/query";

            var response = await _httpClient.PostAsJsonAsync(url, pythonRequest, cancellationToken);

            response.EnsureSuccessStatusCode();

            var pythonResponse = await response.Content.ReadFromJsonAsync<PythonLlmResponse>(cancellationToken);

            if (pythonResponse == null)
            {
                throw new InvalidOperationException("Received null response from Python service");
            }

            var result = MapToQueryResponse(pythonResponse, request.LlmModel);

            _logger.LogInformation(
                "Successfully received LLM response for chat {ChatHistoryId}, processing time: {ProcessingTime}ms",
                request.ChatHistoryId, result.Metadata.ProcessingTimeMs);

            return result;
        }
        catch (HttpRequestException ex)
        {
            _logger.LogError(ex, "HTTP error communicating with Python LLM service");
            throw new Exception("Failed to communicate with LLM service. The service may be unavailable.", ex);
        }
        catch (TaskCanceledException ex)
        {
            _logger.LogError(ex, "Request to Python LLM service timed out");
            throw new Exception("LLM query timed out. Please try again with a simpler query or fewer documents.", ex);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Unexpected error during LLM query");
            throw;
        }
    }

    public async IAsyncEnumerable<string> QueryStreamAsync(
        LlmQueryRequestDto request,
        [EnumeratorCancellation] CancellationToken cancellationToken = default)
    {
        _logger.LogInformation(
            "Starting streaming LLM query for workspace {WorkspaceId}, chat {ChatHistoryId}, model {Model}",
            request.WorkspaceId, request.ChatHistoryId, request.LlmModel);

        var pythonRequest = MapToPythonRequest(request);
        var url = $"{_pythonServiceUrl}/api/llm/query";

        using var requestMessage = new HttpRequestMessage(HttpMethod.Post, url)
        {
            Content = JsonContent.Create(pythonRequest)
        };

        requestMessage.Headers.Accept.Add(new System.Net.Http.Headers.MediaTypeWithQualityHeaderValue("text/event-stream"));

        // Use a separate method to handle the streaming logic without try-catch around yield
        await foreach (var chunk in StreamResponseAsync(requestMessage, request.ChatHistoryId, cancellationToken))
        {
            yield return chunk;
        }
    }

    private async IAsyncEnumerable<string> StreamResponseAsync(
        HttpRequestMessage requestMessage,
        Guid chatHistoryId,
        [EnumeratorCancellation] CancellationToken cancellationToken = default)
    {
        HttpResponseMessage? response = null;
        Stream? stream = null;
        StreamReader? reader = null;

        Exception? capturedException = null;

        try
        {
            response = await _httpClient.SendAsync(requestMessage, HttpCompletionOption.ResponseHeadersRead, cancellationToken);
            response.EnsureSuccessStatusCode();

            stream = await response.Content.ReadAsStreamAsync(cancellationToken);
            reader = new StreamReader(stream);
        }
        catch (HttpRequestException ex)
        {
            _logger.LogError(ex, "HTTP error during streaming query");
            capturedException = ex;
        }
        catch (TaskCanceledException ex)
        {
            _logger.LogError(ex, "Streaming query timed out or was cancelled");
            capturedException = ex;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Unexpected error during streaming query");
            capturedException = ex;
        }

        if (capturedException != null)
        {
            var errorMessage = capturedException switch
            {
                HttpRequestException => "Failed to communicate with LLM service. The service may be unavailable.",
                TaskCanceledException => "Request timed out or was cancelled.",
                _ => $"An unexpected error occurred: {capturedException.Message}"
            };

            var errorData = JsonSerializer.Serialize(new StreamChunk
            {
                Type = "error",
                Message = errorMessage
            });

            yield return $"data: {errorData}\n\n";
            yield break;
        }

        if (reader == null)
        {
            yield break;
        }

        try
        {
            while (!reader.EndOfStream && !cancellationToken.IsCancellationRequested)
            {
                var line = await reader.ReadLineAsync(cancellationToken);

                if (string.IsNullOrWhiteSpace(line))
                {
                    continue;
                }

                // SSE format: "data: {json}\n\n"
                if (line.StartsWith("data: "))
                {
                    var jsonData = line.Substring(6); // Remove "data: " prefix

                    StreamChunk? chunk = null;
                    try
                    {
                        chunk = JsonSerializer.Deserialize<StreamChunk>(jsonData);
                    }
                    catch (JsonException ex)
                    {
                        _logger.LogWarning(ex, "Failed to parse streaming chunk: {Data}", jsonData);
                        continue;
                    }

                    if (chunk != null)
                    {
                        // Convert chunk to SSE format for client
                        var sseData = $"data: {jsonData}\n\n";
                        yield return sseData;

                        // Log completion
                        if (chunk.Type == "done")
                        {
                            _logger.LogInformation(
                                "Completed streaming LLM response for chat {ChatHistoryId}",
                                chatHistoryId);
                            break;
                        }

                        // Log errors
                        if (chunk.Type == "error")
                        {
                            _logger.LogError(
                                "Error in streaming response: {ErrorMessage}",
                                chunk.Message);
                        }
                    }
                }
            }
        }
        finally
        {
            reader?.Dispose();
            stream?.Dispose();
            response?.Dispose();
        }
    }

    public async Task<bool> IsServiceAvailableAsync(CancellationToken cancellationToken = default)
    {
        try
        {
            var url = $"{_pythonServiceUrl}/health";
            var response = await _httpClient.GetAsync(url, cancellationToken);
            return response.IsSuccessStatusCode;
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "Python LLM service health check failed");
            return false;
        }
    }

    private static PythonLlmRequest MapToPythonRequest(LlmQueryRequestDto request)
    {
        return new PythonLlmRequest
        {
            Query = request.Query,
            WorkspaceId = request.WorkspaceId.ToString(),
            PdfIds = request.SelectedPdfIds.Select(id => id.ToString()).ToArray(),
            ChatHistoryId = request.ChatHistoryId.ToString(),
            ModelName = request.LlmModel,
            ChatHistory = new List<ChatMessage>() // Can be populated from database if needed
        };
    }

    private static LlmQueryResponseDto MapToQueryResponse(PythonLlmResponse pythonResponse, string modelUsed)
    {
        return new LlmQueryResponseDto
        {
            Answer = pythonResponse.Answer,
            References = pythonResponse.References.Select(r => new SourceReference
            {
                PdfName = r.Pdf,
                PageNumber = r.Page,
                PdfId = Guid.Empty // Will need to be mapped from PDF name if required
            }).ToArray(),
            Metadata = new ProcessingMetadata
            {
                ModelUsed = modelUsed,
                Timestamp = DateTime.UtcNow,
                TokenCount = 0, // Can be added if Python service provides it
                ProcessingTimeMs = 0 // Can be calculated if needed
            }
        };
    }

    // Response model from Python service for non-streaming
    private record PythonLlmResponse
    {
        public string Answer { get; init; } = string.Empty;
        public List<PythonSourceReference> References { get; init; } = new();
    }
}
