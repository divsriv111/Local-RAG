namespace API.Middleware;

/// <summary>
/// Middleware to generate and track correlation IDs across requests for distributed tracing
/// </summary>
public class CorrelationIdMiddleware
{
    private const string CorrelationIdHeaderName = "X-Correlation-ID";
    private readonly RequestDelegate _next;
    private readonly ILogger<CorrelationIdMiddleware> _logger;

    public CorrelationIdMiddleware(RequestDelegate next, ILogger<CorrelationIdMiddleware> logger)
    {
        _next = next;
        _logger = logger;
    }

    public async Task InvokeAsync(HttpContext context)
    {
        // Try to get correlation ID from request header
        var correlationId = context.Request.Headers[CorrelationIdHeaderName].FirstOrDefault();

        // If not provided, generate a new one
        if (string.IsNullOrEmpty(correlationId))
        {
            correlationId = Guid.NewGuid().ToString();
        }

        // Add to response headers so client can track the request
        context.Response.OnStarting(() =>
        {
            context.Response.Headers.TryAdd(CorrelationIdHeaderName, correlationId);
            return Task.CompletedTask;
        });

        // Add to HttpContext items so it's accessible throughout the request pipeline
        context.Items[CorrelationIdHeaderName] = correlationId;

        // Add to Serilog log context
        using (Serilog.Context.LogContext.PushProperty("CorrelationId", correlationId))
        {
            _logger.LogInformation("Request started: {Method} {Path}", 
                context.Request.Method, 
                context.Request.Path);

            try
            {
                await _next(context);
            }
            finally
            {
                _logger.LogInformation("Request completed: {Method} {Path} - Status: {StatusCode}", 
                    context.Request.Method, 
                    context.Request.Path,
                    context.Response.StatusCode);
            }
        }
    }
}

/// <summary>
/// Extension method to register the CorrelationIdMiddleware
/// </summary>
public static class CorrelationIdMiddlewareExtensions
{
    public static IApplicationBuilder UseCorrelationId(this IApplicationBuilder builder)
    {
        return builder.UseMiddleware<CorrelationIdMiddleware>();
    }
}
