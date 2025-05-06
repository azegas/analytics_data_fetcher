using ADF.DataAccess.Entities;
using Microsoft.EntityFrameworkCore;

namespace ADF.DataAccess

{
    public class Context : DbContext
    {
        public Context(DbContextOptions<Context> options) : base(options) { }
        public DbSet<JobAdd> JobAdds { get; set; }
    }
}