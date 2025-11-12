namespace Application.Interfaces;

/// <summary>
/// Interface for structured application logging
/// </summary>
public interface IApplicationLoggingService
{
    /// <summary>
    /// Log user authentication attempt
    /// </summary>
    void LogAuthenticationAttempt(string username, bool success, string? errorMessage = null);

    /// <summary>
    /// Log user registration
    /// </summary>
    void LogUserRegistration(string username, string email, bool success, string? errorMessage = null);

    /// <summary>
    /// Log workspace creation
    /// </summary>
    void LogWorkspaceCreated(Guid workspaceId, string workspaceName, Guid userId);

    /// <summary>
    /// Log workspace update
    /// </summary>
    void LogWorkspaceUpdated(Guid workspaceId, string oldName, string newName, Guid userId);

    /// <summary>
    /// Log workspace deletion
    /// </summary>
    void LogWorkspaceDeleted(Guid workspaceId, string workspaceName, Guid userId);

    /// <summary>
    /// Log PDF upload start
    /// </summary>
    void LogPdfUploadStarted(Guid workspaceId, string fileName, long fileSize, Guid userId);

    /// <summary>
    /// Log PDF upload completion
    /// </summary>
    void LogPdfUploadCompleted(Guid pdfId, Guid workspaceId, string fileName, long fileSize, TimeSpan duration, bool success, string? errorMessage = null);

    /// <summary>
    /// Log LLM query start
    /// </summary>
    void LogLlmQueryStarted(Guid chatHistoryId, string model, int queryLength, Guid workspaceId, List<Guid> selectedPdfIds);

    /// <summary>
    /// Log LLM query completion
    /// </summary>
    void LogLlmQueryCompleted(Guid chatHistoryId, string model, int queryLength, int responseLength, TimeSpan responseTime, bool success, string? errorMessage = null);

    /// <summary>
    /// Log exceptions with context
    /// </summary>
    void LogException(Exception exception, string context, Dictionary<string, object>? additionalData = null);

    /// <summary>
    /// Log chat history creation
    /// </summary>
    void LogChatHistoryCreated(Guid chatHistoryId, Guid workspaceId, string chatName, Guid userId);

    /// <summary>
    /// Log chat history deletion
    /// </summary>
    void LogChatHistoryDeleted(Guid chatHistoryId, string chatName, Guid workspaceId, Guid userId);

    /// <summary>
    /// Log chat history archive/unarchive
    /// </summary>
    void LogChatHistoryArchived(Guid chatHistoryId, string chatName, bool isArchived, Guid userId);
}
