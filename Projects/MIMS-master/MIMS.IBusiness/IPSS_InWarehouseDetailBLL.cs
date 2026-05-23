using MIMS.Entity.Model;
using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace MIMS.IBusiness
{
    public interface IPSS_InWarehouseDetailBLL
    {
        /// <summary>
        /// list
        /// </summary>
        /// <returns></returns>
        IList GetList(Hashtable ht);
        IList GetPageList(string query, string orderField, string orderType, int pageIndex, int pageSize, ref int count);

        /// <summary>
        /// 
        /// </summary>
        /// <param name="id"></param>
        /// <returns></returns>
        PSS_InWarehouseDetail GetEntity(string id);
        int Insert(PSS_InWarehouseDetail obj);
        int Delete(PSS_InWarehouseDetail obj);
        IList SearchPhaListByDate(string startDate, string endDate, Hashtable ht, string orderField, string orderType, int pageIndex, int pageSize, ref int count);

    }
}
