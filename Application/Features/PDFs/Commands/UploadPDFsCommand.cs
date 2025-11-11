using Application.DTOs;
using MediatR;
using Microsoft.AspNetCore.Http;

namespace Application.Features.PDFs.Commands;

public record UploadPDFsCommand(
    Guid WorkspaceId,
    Guid UserId,
    IFormFileCollection Files,
    long MaxFileSizeBytes
) : IRequest<BulkUploadResponseDto>;
