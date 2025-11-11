using Microsoft.AspNetCore.Http;

namespace Application.Interfaces;

public interface IFileStorageService
{
    Task<string> SaveFileAsync(IFormFile file, Guid workspaceId, Guid fileId, CancellationToken cancellationToken = default);
    Task<bool> DeleteFileAsync(string filePath, CancellationToken cancellationToken = default);
    Task<bool> EnsureDirectoryExistsAsync(string directoryPath, CancellationToken cancellationToken = default);
    string GetUploadPath(Guid workspaceId, Guid fileId, string fileName);
}
