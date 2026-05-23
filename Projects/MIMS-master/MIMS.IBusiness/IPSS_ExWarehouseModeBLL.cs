using MIMS.Entity.Model;
using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace MIMS.IBusiness
{
    public interface IPSS_ExWarehouseModeBLL
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
        PSS_ExWarehouseMode GetEntity(string id);

        int Update(PSS_ExWarehouseMode obj);

        int Insert(PSS_ExWarehouseMode obj);
        int Delete(PSS_ExWarehouseMode obj);
    }
}
