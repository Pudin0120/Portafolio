using MIMS.Entity.Model;
using System;
using System.Collections.Generic;
using System.Collections;
using System.Configuration;
using System.Data;
using System.Data.SqlClient;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Dapper;

namespace MIMS.Service
{
    public class PHA_DispenseWayDAL
    {

        #region init dbconnection
        private static readonly string connString = ConfigurationManager.ConnectionStrings["PharmacySystem"].ConnectionString;
        private IDbConnection _conn;
        public IDbConnection Conn
        {
            get
            {
                _conn = new SqlConnection(connString);
                _conn.Open();
                return _conn;
            }
        }
        #endregion

        /// <summary>
        /// list
        /// </summary>
        /// <returns></returns>
        public IList GetList()
        {
            using (Conn)
            {
                string query = "SELECT * FROM PHA_DispenseWay";
                return Conn.Query<PHA_DispenseWay>(query).ToList();
            }

        }
        /// <summary>
        /// 
        /// </summary>
        /// <param name="where"></param>
        /// <returns></returns>
        public IList GetList(string where)
        {
            using (Conn)
            {
                string query = "SELECT * FROM PHA_DispenseWay WHERE 1=1 AND";
                query += where;
                return Conn.Query<PHA_DispenseWay>(query).ToList();
            }

        }
    }
}
