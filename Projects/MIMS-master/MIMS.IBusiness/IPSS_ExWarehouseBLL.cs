using MIMS.Entity.Model;
using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace MIMS.IBusiness
{
    public interface IPSS_ExWarehouseBLL
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
        PSS_ExWarehouse GetEntity(string id);

        int Update(PSS_ExWarehouse obj);

        int Insert(PSS_ExWarehouse obj);
        int Delete(PSS_ExWarehouse obj);
    }
}
