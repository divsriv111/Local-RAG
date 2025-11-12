using Application.DTOs;

namespace Application.Interfaces;

public interface ILlmService
{
    /// <summary>
    /// Sends a query to the Python LLM service and returns the complete response.
    /// </summary>
    Task<LlmQueryResponseDto> QueryAsync(LlmQueryRequestDto request, CancellationToken cancellationToken = default);

    /// <summary>
    /// Sends a query to the Python LLM service and streams the response using Server-Sent Events.
    /// </summary>
    IAsyncEnumerable<string> QueryStreamAsync(LlmQueryRequestDto request, CancellationToken cancellationToken = default);

    /// <summary>
    /// Checks if the Python LLM service is available.
    /// </summary>
    Task<bool> IsServiceAvailableAsync(CancellationToken cancellationToken = default);
}
