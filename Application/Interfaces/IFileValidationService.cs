using Microsoft.AspNetCore.Http;

namespace Application.Interfaces;

public interface IFileValidationService
{
    Task<(bool IsValid, string? ErrorMessage)> ValidatePdfFileAsync(IFormFile file, long maxFileSizeBytes);
    bool IsPdfFile(IFormFile file);
    string GetFileExtension(string fileName);
}
