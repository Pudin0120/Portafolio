using MIMS.Entity.Model;
using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace MIMS.IBusiness
{
    public interface IPSS_PurchasePlanBLL
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
        PSS_PurchasePlan GetEntity(string id);

        int Update(PSS_PurchasePlan obj);

        int Insert(PSS_PurchasePlan obj);
        int Delete(PSS_PurchasePlan obj);
    }
}
