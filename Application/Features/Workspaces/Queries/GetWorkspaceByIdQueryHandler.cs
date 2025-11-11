using Application.DTOs;
using Domain.Common;
using Domain.Entities;
using MediatR;

namespace Application.Features.Workspaces.Queries;

public class GetWorkspaceByIdQueryHandler : IRequestHandler<GetWorkspaceByIdQuery, WorkspaceDetailDto?>
{
    private readonly IRepository<Workspace> _workspaceRepository;
    private readonly IRepository<ChatHistory> _chatHistoryRepository;
    private readonly IRepository<PDFDocument> _pdfDocumentRepository;

    public GetWorkspaceByIdQueryHandler(
        IRepository<Workspace> workspaceRepository,
        IRepository<ChatHistory> chatHistoryRepository,
        IRepository<PDFDocument> pdfDocumentRepository)
    {
        _workspaceRepository = workspaceRepository;
        _chatHistoryRepository = chatHistoryRepository;
        _pdfDocumentRepository = pdfDocumentRepository;
    }

    public async Task<WorkspaceDetailDto?> Handle(GetWorkspaceByIdQuery request, CancellationToken cancellationToken)
    {
        var workspace = await _workspaceRepository.GetByIdAsync(request.Id, cancellationToken);

        if (workspace == null || workspace.UserId != request.UserId)
            return null;

        var chatHistories = (await _chatHistoryRepository.GetAllAsync(cancellationToken))
            .Where(ch => ch.WorkspaceId == workspace.Id)
            .OrderByDescending(ch => ch.CreatedAt);

        var pdfDocuments = (await _pdfDocumentRepository.GetAllAsync(cancellationToken))
            .Where(pdf => pdf.WorkspaceId == workspace.Id)
            .OrderByDescending(pdf => pdf.UploadedAt);

        return new WorkspaceDetailDto
        {
            Id = workspace.Id,
            Name = workspace.Name,
            UserId = workspace.UserId,
            CreatedAt = workspace.CreatedAt,
            UpdatedAt = workspace.UpdatedAt,
            ChatHistories = chatHistories.Select(ch => new ChatHistoryDto
            {
                Id = ch.Id,
                WorkspaceId = ch.WorkspaceId,
                Name = ch.Name,
                FirstQuery = ch.FirstQuery,
                CreatedAt = ch.CreatedAt,
                IsArchived = ch.IsArchived,
                MessageCount = ch.Messages.Count
            }).ToList(),
            PDFDocuments = pdfDocuments.Select(pdf => new PDFDocumentDto
            {
                Id = pdf.Id,
                WorkspaceId = pdf.WorkspaceId,
                FileName = pdf.FileName,
                FilePath = pdf.FilePath,
                FileSize = pdf.FileSize,
                UploadedAt = pdf.UploadedAt,
                IsSelected = pdf.IsSelected
            }).ToList()
        };
    }
}
