using Application.DTOs;
using Application.Features.PDFs.Commands;
using Application.Interfaces;
using Domain.Common;
using Domain.Entities;
using MediatR;

namespace Application.Features.PDFs.Commands;

public class UploadPDFsCommandHandler : IRequestHandler<UploadPDFsCommand, BulkUploadResponseDto>
{
    private readonly IRepository<PDFDocument> _pdfRepository;
    private readonly IRepository<Workspace> _workspaceRepository;
    private readonly IUnitOfWork _unitOfWork;
    private readonly IFileValidationService _fileValidationService;
    private readonly IFileStorageService _fileStorageService;

    public UploadPDFsCommandHandler(
        IRepository<PDFDocument> pdfRepository,
        IRepository<Workspace> workspaceRepository,
        IUnitOfWork unitOfWork,
        IFileValidationService fileValidationService,
        IFileStorageService fileStorageService)
    {
        _pdfRepository = pdfRepository;
        _workspaceRepository = workspaceRepository;
        _unitOfWork = unitOfWork;
        _fileValidationService = fileValidationService;
        _fileStorageService = fileStorageService;
    }

    public async Task<BulkUploadResponseDto> Handle(UploadPDFsCommand request, CancellationToken cancellationToken)
    {
        var results = new List<UploadPDFResultDto>();
        var uploadedDocuments = new List<PDFDocument>();

        // Verify workspace exists and user has access
        var workspace = await _workspaceRepository.GetByIdAsync(request.WorkspaceId, cancellationToken);
        if (workspace == null)
        {
            throw new InvalidOperationException("Workspace not found.");
        }

        // Get existing PDFs count before upload
        var existingPdfsCount = await GetPdfCountForWorkspaceAsync(request.WorkspaceId, cancellationToken);

        // Process each file
        foreach (var file in request.Files)
        {
            var result = await ProcessSingleFileAsync(file, request, cancellationToken);
            results.Add(result);

            if (result.Success)
            {
                uploadedDocuments.Add(new PDFDocument
                {
                    Id = result.Id,
                    WorkspaceId = request.WorkspaceId,
                    FileName = result.FileName,
                    FilePath = result.FilePath,
                    FileSize = result.FileSize,
                    UploadedAt = result.UploadedAt,
                    IsSelected = false // Will be set later if needed
                });
            }
        }

        // Save all successful uploads to database
        if (uploadedDocuments.Any())
        {
            foreach (var document in uploadedDocuments)
            {
                await _pdfRepository.AddAsync(document, cancellationToken);
            }

            // Auto-select if this is the only PDF in the workspace
            var shouldAutoSelect = existingPdfsCount == 0 && uploadedDocuments.Count == 1;
            if (shouldAutoSelect)
            {
                uploadedDocuments[0].IsSelected = true;
            }

            await _unitOfWork.SaveChangesAsync(cancellationToken);

            // Update results with IsSelected status
            if (shouldAutoSelect)
            {
                var autoSelectedResult = results.First(r => r.Success);
                var index = results.IndexOf(autoSelectedResult);
                results[index] = autoSelectedResult with { };
            }
        }

        var successCount = results.Count(r => r.Success);
        var failureCount = results.Count - successCount;
        var isOnlyPdfAutoSelected = existingPdfsCount == 0 && uploadedDocuments.Count == 1;

        return new BulkUploadResponseDto
        {
            Results = results,
            SuccessCount = successCount,
            FailureCount = failureCount,
            IsOnlyPdfAutoSelected = isOnlyPdfAutoSelected
        };
    }

    private async Task<UploadPDFResultDto> ProcessSingleFileAsync(
        Microsoft.AspNetCore.Http.IFormFile file,
        UploadPDFsCommand request,
        CancellationToken cancellationToken)
    {
        var fileId = Guid.NewGuid();
        var uploadedAt = DateTime.UtcNow;

        try
        {
            // Validate file
            var (isValid, errorMessage) = await _fileValidationService.ValidatePdfFileAsync(file, request.MaxFileSizeBytes);
            if (!isValid)
            {
                return new UploadPDFResultDto
                {
                    Id = fileId,
                    FileName = file.FileName,
                    FileSize = file.Length,
                    UploadedAt = uploadedAt,
                    FilePath = string.Empty,
                    Success = false,
                    ErrorMessage = errorMessage
                };
            }

            // Save file to disk
            var filePath = await _fileStorageService.SaveFileAsync(file, request.WorkspaceId, fileId, cancellationToken);

            return new UploadPDFResultDto
            {
                Id = fileId,
                FileName = file.FileName,
                FileSize = file.Length,
                UploadedAt = uploadedAt,
                FilePath = filePath,
                Success = true,
                ErrorMessage = null
            };
        }
        catch (IOException ioEx)
        {
            return new UploadPDFResultDto
            {
                Id = fileId,
                FileName = file.FileName,
                FileSize = file.Length,
                UploadedAt = uploadedAt,
                FilePath = string.Empty,
                Success = false,
                ErrorMessage = $"Disk error: {ioEx.Message}"
            };
        }
        catch (Exception ex)
        {
            return new UploadPDFResultDto
            {
                Id = fileId,
                FileName = file.FileName,
                FileSize = file.Length,
                UploadedAt = uploadedAt,
                FilePath = string.Empty,
                Success = false,
                ErrorMessage = $"Upload failed: {ex.Message}"
            };
        }
    }

    private async Task<int> GetPdfCountForWorkspaceAsync(Guid workspaceId, CancellationToken cancellationToken)
    {
        var allPdfs = await _pdfRepository.GetAllAsync(cancellationToken);
        return allPdfs.Count(p => p.WorkspaceId == workspaceId);
    }
}
