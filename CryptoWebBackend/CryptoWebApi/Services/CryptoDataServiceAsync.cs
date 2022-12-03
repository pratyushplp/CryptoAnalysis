using CryptoWebApi.Data;
using CryptoWebApi.Models;
using CryptoWebApi.Services.Wrapper;
using Microsoft.EntityFrameworkCore;

namespace CryptoWebApi.Services;

public class CryptoDataServiceAsync: ICryptoDataServiceAsync
{
    private DataContext _dbContext;

    public CryptoDataServiceAsync(DataContext dbContext,IHttpContextAccessor httpContextAccessor)
    {
        _dbContext = dbContext;
        
    }
    
    public async Task<ServiceResponse<List<CryptoData>>> GetCryptoBySymbol(string symbol, DateTime startTime, DateTime closeTime)
    {
        ServiceResponse<List<CryptoData>> serviceResponse = new ServiceResponse<List<CryptoData>>();

        try
        {
            serviceResponse.Data  = await _dbContext.CryptoData.Where(x => x.StartTime >= startTime && x.CloseTime <= closeTime)
                                                                .OrderBy(x=>x.StartTime).ToListAsync();
        }
        catch (Exception e)
        {
            Console.WriteLine(e);
            throw;
        }

        return serviceResponse;
    }
    
    public async Task<ServiceResponse<List<OHLCV>>> GetOHLCVBySymbol(string symbol, DateTime startTime, DateTime closeTime)
    {
        ServiceResponse<List<OHLCV>> serviceResponse = new ServiceResponse<List<OHLCV>>();

        try
        {
            var tempData  = await _dbContext.CryptoData
                                                    .Where(x => x.StartTime >= startTime && x.CloseTime <= closeTime)
                                                    .OrderBy(x=>x.StartTime).ToListAsync();
            serviceResponse.Data = OHLCV.covertDataToOHLCV(tempData);
        }
        catch (Exception e)
        {
            Console.WriteLine(e);
            throw;
        }

        return serviceResponse;
    }

    public Task<ServiceResponse<List<CryptoData>>> GetMultipleCryptoBySymbol(List<string> symbols, DateTime startTime, DateTime closeTime)
    {
        throw new NotImplementedException();
    }
}