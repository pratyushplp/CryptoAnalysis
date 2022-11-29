using CryptoWebApi.Services;
using Microsoft.AspNetCore.Mvc;

namespace CryptoWebApi.Controllers;

[ApiController]
[Route("[controller]")]
public class CryptoDataController : ControllerBase
{
    
    private readonly ILogger<CryptoDataController> _logger;
    private readonly ICryptoDataServiceAsync _cryptoDataServiceAsync;

    public CryptoDataController(ILogger<CryptoDataController> logger, ICryptoDataServiceAsync cryptoDataServiceAsync  )
    {
        _cryptoDataServiceAsync = cryptoDataServiceAsync;
        _logger = logger;
    }

    [HttpGet(Name = "GetCryptoData")]
    public async Task<IActionResult> Get(string symbol, DateTime startDate, DateTime closeDate)
    {
        var value = await _cryptoDataServiceAsync.GetCryptoBySymbol(symbol,startDate,closeDate);
        if (value.Data == null) 
            return NotFound(value);
        return Ok(value);
    }
}
