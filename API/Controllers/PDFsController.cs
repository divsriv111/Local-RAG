using System.Security.Claims;
using Application.DTOs;
using Application.Features.PDFs.Commands;
using MediatR;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace API.Controllers;

[ApiController]
[Route("api/workspaces/{workspaceId}/pdfs")]
[Authorize]
public class PDFsController : ControllerBase
{
    private readonly IMediator _mediator;
    private readonly IConfiguration _configuration;
    private readonly ILogger<PDFsController> _logger;

    public PDFsController(IMediator mediator, IConfiguration configuration, ILogger<PDFsController> logger)
    {
        _mediator = mediator;
        _configuration = configuration;
        _logger = logger;
    }

    private Guid GetAuthenticatedUserId()
    {
        var userIdClaim = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        if (string.IsNullOrEmpty(userIdClaim) || !Guid.TryParse(userIdClaim, out var userId))
        {
            throw new UnauthorizedAccessException("Invalid user token.");
        }
        return userId;
    }

    /// <summary>
    /// Upload multiple PDF files to a workspace
    /// </summary>
    /// <param name="workspaceId">The workspace ID</param>
    /// <param name="files">The PDF files to upload (multipart/form-data)</param>
    /// <returns>Upload results for each file</returns>
    [HttpPost("upload")]
    [RequestSizeLimit(524288000)] // 500 MB total request size
    [RequestFormLimits(MultipartBodyLengthLimit = 524288000)]
    [Consumes("multipart/form-data")]
    [ProducesResponseType(typeof(BulkUploadResponseDto), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status413PayloadTooLarge)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<BulkUploadResponseDto>> Upload(
        [FromRoute] Guid workspaceId,
        [FromForm] IFormFileCollection files)
    {
        try
        {
            // Validate request
            if (files == null || files.Count == 0)
            {
                return BadRequest(new { message = "No files were provided for upload." });
            }

            var userId = GetAuthenticatedUserId();

            // Get max file size from configuration (default 50MB)
            var maxFileSizeMB = _configuration.GetValue<int>("FileStorage:MaxFileSizeMB", 50);
            var maxFileSizeBytes = maxFileSizeMB * 1024L * 1024L;

            _logger.LogInformation(
                "User {UserId} is uploading {FileCount} file(s) to workspace {WorkspaceId}",
                userId, files.Count, workspaceId);

            // Create and send command
            var command = new UploadPDFsCommand(
                workspaceId,
                userId,
                files,
                maxFileSizeBytes
            );

            var result = await _mediator.Send(command);

            // Log results
            _logger.LogInformation(
                "Upload completed for workspace {WorkspaceId}: {SuccessCount} succeeded, {FailureCount} failed",
                workspaceId, result.SuccessCount, result.FailureCount);

            // Return appropriate status code
            if (result.FailureCount == 0)
            {
                return Ok(result);
            }
            else if (result.SuccessCount == 0)
            {
                return BadRequest(result);
            }
            else
            {
                // Partial success
                return Ok(result);
            }
        }
        catch (UnauthorizedAccessException)
        {
            return Unauthorized(new { message = "Invalid authentication token." });
        }
        catch (InvalidOperationException ex) when (ex.Message.Contains("Workspace not found"))
        {
            return NotFound(new { message = "Workspace not found or you don't have access to it." });
        }
        catch (IOException ex) when (ex.Message.Contains("Insufficient disk space"))
        {
            _logger.LogError(ex, "Insufficient disk space for upload to workspace {WorkspaceId}", workspaceId);
            return StatusCode(StatusCodes.Status507InsufficientStorage, new
            {
                message = "Insufficient disk space to complete the upload.",
                error = ex.Message
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Unexpected error during PDF upload to workspace {WorkspaceId}", workspaceId);
            return StatusCode(StatusCodes.Status500InternalServerError, new
            {
                message = "An unexpected error occurred during file upload.",
                error = ex.Message
            });
        }
    }

    /// <summary>
    /// Get upload progress (placeholder for future implementation with SignalR)
    /// </summary>
    [HttpGet("upload/progress/{uploadId}")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public ActionResult GetUploadProgress(Guid uploadId)
    {
        // This is a placeholder for future implementation with SignalR or Server-Sent Events
        // For now, the upload is handled synchronously
        return Ok(new
        {
            uploadId,
            status = "completed",
            message = "Upload progress tracking will be implemented in a future version."
        });
    }
}
