using CryptoWebApi.Models;
using CryptoWebApi.Services;
using CryptoWebApi.Services.Wrapper;
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
    public async Task<IActionResult> GetCryptoData(string symbol, string startDate, string closeDate,string dataType = "")
    {
        dynamic value;
        if ( !string.IsNullOrWhiteSpace(dataType) && dataType.ToLower().Equals("ohlcv"))
        {
            value = await _cryptoDataServiceAsync.GetOHLCVBySymbol(symbol,
                DateTime.Parse(startDate), DateTime.Parse(closeDate));
        }
        else
        {
            value = await _cryptoDataServiceAsync.GetCryptoBySymbol(symbol,
                DateTime.Parse(startDate), DateTime.Parse(closeDate));
        }
        
        if (value.Data == null) 
            return NotFound(value);
        return Ok(value);
    }

    
}
