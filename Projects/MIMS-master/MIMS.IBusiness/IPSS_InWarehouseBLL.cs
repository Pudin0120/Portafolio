using MIMS.Entity.Model;
using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;


namespace MIMS.IBusiness
{
    public interface IPSS_InWarehouseBLL
    {
        /// <summary>
        /// list
        /// </summary>
        /// <returns></returns>
        IList GetList();

        /// <summary>
        /// 
        /// </summary>
        /// <param name="id"></param>
        /// <returns></returns>
        PSS_InWarehouse GetEntity(string id);

        int Update(PSS_InWarehouse obj);

        int Insert(PSS_InWarehouse obj);
        int Delete(PSS_InWarehouse obj);
    }
}
