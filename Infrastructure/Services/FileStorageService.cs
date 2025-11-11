using Application.Interfaces;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Configuration;

namespace Infrastructure.Services;

public class FileStorageService : IFileStorageService
{
    private readonly string _uploadBasePath;

    public FileStorageService(IConfiguration configuration)
    {
        _uploadBasePath = configuration["FileStorage:UploadPath"] ?? "uploads";

        // Ensure the base upload directory exists
        if (!Directory.Exists(_uploadBasePath))
        {
            Directory.CreateDirectory(_uploadBasePath);
        }
    }

    public async Task<string> SaveFileAsync(IFormFile file, Guid workspaceId, Guid fileId, CancellationToken cancellationToken = default)
    {
        try
        {
            var filePath = GetUploadPath(workspaceId, fileId, file.FileName);
            var directoryPath = Path.GetDirectoryName(filePath);

            if (string.IsNullOrEmpty(directoryPath))
            {
                throw new InvalidOperationException("Unable to determine directory path.");
            }

            // Ensure directory exists
            await EnsureDirectoryExistsAsync(directoryPath, cancellationToken);

            // Check available disk space before saving
            var driveInfo = new DriveInfo(Path.GetPathRoot(filePath) ?? "/");
            if (driveInfo.AvailableFreeSpace < file.Length)
            {
                throw new IOException("Insufficient disk space to save the file.");
            }

            // Save the file
            await using var fileStream = new FileStream(filePath, FileMode.Create, FileAccess.Write, FileShare.None, 8192, useAsync: true);
            await file.CopyToAsync(fileStream, cancellationToken);

            return filePath;
        }
        catch (Exception ex)
        {
            throw new IOException($"Failed to save file: {ex.Message}", ex);
        }
    }

    public async Task<bool> DeleteFileAsync(string filePath, CancellationToken cancellationToken = default)
    {
        try
        {
            if (File.Exists(filePath))
            {
                await Task.Run(() => File.Delete(filePath), cancellationToken);
                return true;
            }
            return false;
        }
        catch
        {
            return false;
        }
    }

    public Task<bool> EnsureDirectoryExistsAsync(string directoryPath, CancellationToken cancellationToken = default)
    {
        try
        {
            if (!Directory.Exists(directoryPath))
            {
                Directory.CreateDirectory(directoryPath);
            }
            return Task.FromResult(true);
        }
        catch
        {
            return Task.FromResult(false);
        }
    }

    public string GetUploadPath(Guid workspaceId, Guid fileId, string fileName)
    {
        var extension = Path.GetExtension(fileName);
        var workspaceFolder = Path.Combine(_uploadBasePath, workspaceId.ToString());
        var filePath = Path.Combine(workspaceFolder, $"{fileId}{extension}");
        return filePath;
    }
}
