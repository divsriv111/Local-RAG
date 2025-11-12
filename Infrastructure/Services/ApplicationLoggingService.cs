using Application.Interfaces;
using Microsoft.Extensions.Logging;

namespace Infrastructure.Services;

/// <summary>
/// Structured logging service for custom application events
/// </summary>
public class ApplicationLoggingService : IApplicationLoggingService
{
    private readonly ILogger<ApplicationLoggingService> _logger;

    public ApplicationLoggingService(ILogger<ApplicationLoggingService> logger)
    {
        _logger = logger;
    }

    public void LogAuthenticationAttempt(string username, bool success, string? errorMessage = null)
    {
        if (success)
        {
            _logger.LogInformation(
                "Authentication successful for user: {Username} at {Timestamp}",
                username,
                DateTime.UtcNow);
        }
        else
        {
            _logger.LogWarning(
                "Authentication failed for user: {Username} at {Timestamp}. Reason: {ErrorMessage}",
                username,
                DateTime.UtcNow,
                errorMessage ?? "Invalid credentials");
        }
    }

    public void LogUserRegistration(string username, string email, bool success, string? errorMessage = null)
    {
        if (success)
        {
            _logger.LogInformation(
                "User registered successfully: {Username}, Email: {Email} at {Timestamp}",
                username,
                email,
                DateTime.UtcNow);
        }
        else
        {
            _logger.LogError(
                "User registration failed for {Username}. Reason: {ErrorMessage}",
                username,
                errorMessage ?? "Unknown error");
        }
    }

    public void LogWorkspaceCreated(Guid workspaceId, string workspaceName, Guid userId)
    {
        _logger.LogInformation(
            "Workspace created: {WorkspaceId}, Name: {WorkspaceName}, UserId: {UserId} at {Timestamp}",
            workspaceId,
            workspaceName,
            userId,
            DateTime.UtcNow);
    }

    public void LogWorkspaceUpdated(Guid workspaceId, string oldName, string newName, Guid userId)
    {
        _logger.LogInformation(
            "Workspace updated: {WorkspaceId}, OldName: {OldName}, NewName: {NewName}, UserId: {UserId} at {Timestamp}",
            workspaceId,
            oldName,
            newName,
            userId,
            DateTime.UtcNow);
    }

    public void LogWorkspaceDeleted(Guid workspaceId, string workspaceName, Guid userId)
    {
        _logger.LogInformation(
            "Workspace deleted: {WorkspaceId}, Name: {WorkspaceName}, UserId: {UserId} at {Timestamp}",
            workspaceId,
            workspaceName,
            userId,
            DateTime.UtcNow);
    }

    public void LogPdfUploadStarted(Guid workspaceId, string fileName, long fileSize, Guid userId)
    {
        _logger.LogInformation(
            "PDF upload started: {FileName}, Size: {FileSize} bytes, WorkspaceId: {WorkspaceId}, UserId: {UserId} at {Timestamp}",
            fileName,
            fileSize,
            workspaceId,
            userId,
            DateTime.UtcNow);
    }

    public void LogPdfUploadCompleted(Guid pdfId, Guid workspaceId, string fileName, long fileSize, TimeSpan duration, bool success, string? errorMessage = null)
    {
        if (success)
        {
            _logger.LogInformation(
                "PDF upload completed: {PdfId}, {FileName}, Size: {FileSize} bytes, Duration: {Duration}ms, WorkspaceId: {WorkspaceId} at {Timestamp}",
                pdfId,
                fileName,
                fileSize,
                duration.TotalMilliseconds,
                workspaceId,
                DateTime.UtcNow);
        }
        else
        {
            _logger.LogError(
                "PDF upload failed: {FileName}, Size: {FileSize} bytes, WorkspaceId: {WorkspaceId}, Duration: {Duration}ms. Error: {ErrorMessage}",
                fileName,
                fileSize,
                workspaceId,
                duration.TotalMilliseconds,
                errorMessage ?? "Unknown error");
        }
    }

    public void LogLlmQueryStarted(Guid chatHistoryId, string model, int queryLength, Guid workspaceId, List<Guid> selectedPdfIds)
    {
        _logger.LogInformation(
            "LLM query started: ChatHistoryId: {ChatHistoryId}, Model: {Model}, QueryLength: {QueryLength} chars, WorkspaceId: {WorkspaceId}, SelectedPDFs: {SelectedPdfCount} at {Timestamp}",
            chatHistoryId,
            model,
            queryLength,
            workspaceId,
            selectedPdfIds.Count,
            DateTime.UtcNow);
    }

    public void LogLlmQueryCompleted(Guid chatHistoryId, string model, int queryLength, int responseLength, TimeSpan responseTime, bool success, string? errorMessage = null)
    {
        if (success)
        {
            _logger.LogInformation(
                "LLM query completed: ChatHistoryId: {ChatHistoryId}, Model: {Model}, QueryLength: {QueryLength} chars, ResponseLength: {ResponseLength} chars, ResponseTime: {ResponseTime}ms at {Timestamp}",
                chatHistoryId,
                model,
                queryLength,
                responseLength,
                responseTime.TotalMilliseconds,
                DateTime.UtcNow);
        }
        else
        {
            _logger.LogError(
                "LLM query failed: ChatHistoryId: {ChatHistoryId}, Model: {Model}, QueryLength: {QueryLength} chars, ResponseTime: {ResponseTime}ms. Error: {ErrorMessage}",
                chatHistoryId,
                model,
                queryLength,
                responseTime.TotalMilliseconds,
                errorMessage ?? "Unknown error");
        }
    }

    public void LogException(Exception exception, string context, Dictionary<string, object>? additionalData = null)
    {
        var logProperties = new Dictionary<string, object>
        {
            { "Context", context },
            { "ExceptionType", exception.GetType().Name },
            { "ExceptionMessage", exception.Message },
            { "StackTrace", exception.StackTrace ?? "No stack trace available" },
            { "Timestamp", DateTime.UtcNow }
        };

        if (additionalData != null)
        {
            foreach (var kvp in additionalData)
            {
                logProperties[kvp.Key] = kvp.Value;
            }
        }

        _logger.LogError(
            exception,
            "Exception occurred in {Context}. Exception: {ExceptionType}, Message: {ExceptionMessage}, Additional Data: {@AdditionalData}",
            context,
            exception.GetType().Name,
            exception.Message,
            logProperties);
    }

    public void LogChatHistoryCreated(Guid chatHistoryId, Guid workspaceId, string chatName, Guid userId)
    {
        _logger.LogInformation(
            "Chat history created: {ChatHistoryId}, Name: {ChatName}, WorkspaceId: {WorkspaceId}, UserId: {UserId} at {Timestamp}",
            chatHistoryId,
            chatName,
            workspaceId,
            userId,
            DateTime.UtcNow);
    }

    public void LogChatHistoryDeleted(Guid chatHistoryId, string chatName, Guid workspaceId, Guid userId)
    {
        _logger.LogInformation(
            "Chat history deleted: {ChatHistoryId}, Name: {ChatName}, WorkspaceId: {WorkspaceId}, UserId: {UserId} at {Timestamp}",
            chatHistoryId,
            chatName,
            workspaceId,
            userId,
            DateTime.UtcNow);
    }

    public void LogChatHistoryArchived(Guid chatHistoryId, string chatName, bool isArchived, Guid userId)
    {
        _logger.LogInformation(
            "Chat history {Action}: {ChatHistoryId}, Name: {ChatName}, UserId: {UserId} at {Timestamp}",
            isArchived ? "archived" : "unarchived",
            chatHistoryId,
            chatName,
            userId,
            DateTime.UtcNow);
    }
}
