using CryptoWebApi.Services.Wrapper;
using CryptoWebApi.Models;
namespace CryptoWebApi.Services;

public interface ICryptoDataServiceAsync
{
    public Task<ServiceResponse<List<CryptoData>>> GetCryptoBySymbol (string symbol, DateTime startTime, DateTime closeTime);
    public Task<ServiceResponse<List<OHLCV>>> GetOHLCVBySymbol (string symbol, DateTime startTime, DateTime closeTime);
    public Task<ServiceResponse<List<CryptoData>>> GetMultipleCryptoBySymbol (List<string> symbols,DateTime startTime, DateTime closeTime);

}