using CryptoWebApi.Extra;
using CryptoWebApi.Models;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Infrastructure;

namespace CryptoWebApi.Data;

public class DataContext : DbContext
{
    public string CreateSymbol { get; set; }

    private readonly IHttpContextAccessor _httpContextAccessor;
    
    //Dynamically change table according to the http request
    public DataContext(DbContextOptions<DataContext> options, IHttpContextAccessor httpContextAccessor) : base (options)
    {
        _httpContextAccessor = httpContextAccessor;
        CreateSymbol=_httpContextAccessor?.HttpContext?.Request?.Query["symbol"]??"ETHUSDT";
    }
    
    public DbSet<CryptoData> CryptoData { get; set;}

    
    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<CryptoData>(b =>
        {
            //b.ToTable(CreateSymbol.ToLower());
            b.ToTable(CreateSymbol??"ETHUSDT");
            b.HasKey(p => p.id);
        });
        //modelBuilder.Entity<CryptoData>().ToTable(symbol);
    }
    protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)=> optionsBuilder.ReplaceService<IModelCacheKeyFactory, DynamicModelCacheKeyFactory>();
    
}