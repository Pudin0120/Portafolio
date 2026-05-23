using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using MIMS.Entity.Model;

namespace MIMS.IBusiness
{

    public interface IPSS_InWarehouseModeBLL
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
        PSS_InWarehouseMode GetEntity(string id);

        int Update(PSS_InWarehouseMode obj);

        int Insert(PSS_InWarehouseMode obj);
        int Delete(PSS_InWarehouseMode obj);
    }
}
