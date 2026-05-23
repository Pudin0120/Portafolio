using MIMS.Entity.Model;
using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace MIMS.IBusiness
{
    public interface IPHA_RepositoryBLL
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
        PHA_Repository GetEntity(string id);

        int Update(PHA_Repository obj);

        int Insert(PHA_Repository obj);
        int Delete(PHA_Repository obj);
    }
}
