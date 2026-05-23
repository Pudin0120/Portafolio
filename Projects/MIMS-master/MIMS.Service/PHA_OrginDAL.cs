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
    public class PHA_OrginDAL
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
                string query = "SELECT * FROM PHA_Orgin";
                return Conn.Query<PHA_Orgin>(query).ToList();
            }

        }

         /// <summary>
        /// ()
        /// </summary>
        /// <param name="where"></param>
        /// <param name="orderField"></param>
        /// <param name="prams"></param>
        /// <param name="orderType"></param>
        /// <param name="pageIndex"></param>
        /// <param name="pageSize"></param>
        /// <param name="count"></param>
        /// <returns></returns>
        public IList GetPageListWhere(StringBuilder where, Dictionary<string, object> prams, string orderField, string orderType, int pageIndex, int pageSize, ref int count)
        {
            int num = (pageIndex - 1) * pageSize;
            int num1 = pageIndex * pageSize;
            using (Conn)
            {
                StringBuilder strSql = new StringBuilder();
                StringBuilder sql = new StringBuilder();
                sql.Append(@"SELECT * FROM (SELECT  OrginID,OrginName,PinyinCode,Manufacturer 
                                                FROM PHA_Orgin) A WHERE 1=1 ");
                sql.Append(where);
                strSql.Append("Select * From (Select ROW_NUMBER() Over (Order By " + orderField + " " + orderType + "");
                strSql.Append(") As rowNum, * From (" + sql + ") As T ) As N Where rowNum > " + num + " And rowNum <= " + num1 + "");
                count = Conn.Query<int>("Select Count(1) From (" + sql + ") As t", prams).Single();
                return Conn.Query<PHA_Orgin>(strSql.ToString(), prams).ToList();
            }
        }

        /// <summary>
        /// 
        /// </summary>
        /// <param name="id"></param>
        /// <returns></returns>
        public PHA_Orgin GetEntity(string id)
        {
            using (Conn)
            {
                string query = "SELECT * FROM PHA_Orgin WHERE OrginID=@OrginID";
                return Conn.Query<PHA_Orgin>(query, new { OrginID = id }).SingleOrDefault();
            }
        }

        public int Update(PHA_Orgin obj)
        {
            using (Conn)
            {
                string query = @"UPDATE PHA_Orgin 
                                    SET  OrginName=@OrginName,PinyinCode=@PinyinCode,Manufacturer=@Manufacturer
                                       WHERE OrginID =@OrginID";
                return Conn.Execute(query, obj);
            }
        }
        public int Insert(PHA_Orgin obj)
        {
            using (Conn)
            {
                string query = @"INSERT INTO PHA_Orgin 
                                    VALUES(@OrginName,@PinyinCode,@Manufacturer)";
                return Conn.Execute(query, obj);
            }
        }
        public int Delete(PHA_Orgin obj)
        {
            using (Conn)
            {
                string query = @"DELETE FROM PHA_Orgin WHERE OrginID = @OrginID";
                return Conn.Execute(query, obj);
            }
        }
    }
}
