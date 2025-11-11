using Application.Interfaces;
using Microsoft.AspNetCore.Http;

namespace Infrastructure.Services;

public class FileValidationService : IFileValidationService
{
    private static readonly string[] AllowedContentTypes = { "application/pdf" };
    private static readonly string[] AllowedExtensions = { ".pdf" };

    public async Task<(bool IsValid, string? ErrorMessage)> ValidatePdfFileAsync(IFormFile file, long maxFileSizeBytes)
    {
        // Check if file is null or empty
        if (file == null || file.Length == 0)
        {
            return (false, "File is empty or not provided.");
        }

        // Check file size
        if (file.Length > maxFileSizeBytes)
        {
            var maxSizeMB = maxFileSizeBytes / (1024.0 * 1024.0);
            return (false, $"File size exceeds the maximum allowed size of {maxSizeMB:F2} MB.");
        }

        // Check file extension
        var extension = GetFileExtension(file.FileName).ToLowerInvariant();
        if (!AllowedExtensions.Contains(extension))
        {
            return (false, "Only PDF files are allowed.");
        }

        // Check content type
        if (!AllowedContentTypes.Contains(file.ContentType.ToLowerInvariant()))
        {
            return (false, "Invalid file type. Only PDF files are allowed.");
        }

        // Verify PDF signature (magic bytes)
        var isValidPdf = await VerifyPdfSignatureAsync(file);
        if (!isValidPdf)
        {
            return (false, "File does not appear to be a valid PDF document.");
        }

        return (true, null);
    }

    public bool IsPdfFile(IFormFile file)
    {
        if (file == null)
            return false;

        var extension = GetFileExtension(file.FileName).ToLowerInvariant();
        return AllowedExtensions.Contains(extension) &&
               AllowedContentTypes.Contains(file.ContentType.ToLowerInvariant());
    }

    public string GetFileExtension(string fileName)
    {
        return Path.GetExtension(fileName);
    }

    private async Task<bool> VerifyPdfSignatureAsync(IFormFile file)
    {
        try
        {
            // PDF files start with "%PDF-" (hex: 25 50 44 46 2D)
            var buffer = new byte[5];
            using var stream = file.OpenReadStream();
            var bytesRead = await stream.ReadAsync(buffer, 0, 5);

            // Reset stream position for later use
            stream.Position = 0;

            if (bytesRead < 5)
                return false;

            // Check for PDF signature
            return buffer[0] == 0x25 && // %
                   buffer[1] == 0x50 && // P
                   buffer[2] == 0x44 && // D
                   buffer[3] == 0x46 && // F
                   buffer[4] == 0x2D;   // -
        }
        catch
        {
            return false;
        }
    }
}
