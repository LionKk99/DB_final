<template>
    <div>
      <el-header>
        <div style="text-align: center;">
          <h1>家庭成员</h1>
        </div>
      </el-header>
      <el-main>


        <el-row :gutter="20">
          <el-button type="primary" @click="showadd()">添加</el-button>
          <el-button type="primary" @click="statistics()">统计</el-button>
        </el-row>


        <el-dialog title="添加家庭成员" :visible.sync="dialog_add" width="40%" center>
          <div>
            <el-form ref="form" :model="form_add" label-width="100px">

              <el-form-item label="身份证号：">
                <el-input v-model="form_add.IDNumber"></el-input>
              </el-form-item>

              <el-form-item label="姓名：">
                <el-input v-model="form_add.Name"></el-input>
              </el-form-item>

              <el-form-item label="邮箱：">
                <el-input v-model="form_add.EmailAddress"></el-input>
              </el-form-item>

            </el-form>

            <div style="text-align: center;">
              <el-button type="primary" @click="add()">
                提交
              </el-button>
            </div>

          </div>
        </el-dialog>

        <el-dialog title="统计" :visible.sync="dialog_statistics" width="40%" center>
          <div>
            <el-table :data="tableData_statistics" border style="width: 100%; text-align: center;">
              <el-table-column prop="Name" label="姓名" width="180" align="center"></el-table-column>
              <el-table-column prop="PolicyCount" label="保单数量" width="180" align="center"></el-table-column>
              <el-table-column prop="TotalCoverage" label="总保额" align="center"></el-table-column>
              <el-table-column prop="TotalCost" label="总费用" align="center"></el-table-column>
            </el-table>
            <br>
            <br>
            <br>
            <div style="display: flex; justify-content: center; align-items: center; ">
              <canvas id="myPieChart" style="max-width: 500px; max-height: 500px;"></canvas>
            </div>

          </div>

        </el-dialog>


        <el-table :data="tableData_out" style="width: 100%">
          <el-table-column prop="IDNumber" label="身份证号" align="center"></el-table-column>
          <el-table-column prop="Name" label="姓名" align="center"></el-table-column>
          <el-table-column prop="EmailAddress" label="邮箱" align="center"></el-table-column>
          <el-table-column prop="operate" label="操作" align="center">
            <template slot-scope="scope">
              <el-button type="danger" @click="del(scope.row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-main>
    </div>
</template>

<script>
import Chart from 'chart.js/auto';

export default {
  created() {
    this.getdata();
  },
  data() {
    return {
      tableData_out: [],
      dialog_statistics: false,
      dialog_add: false,
      form_add:{
        IDNumber:'',
        Name:'',
        EmailAddress:'',
      },
      tableData_statistics :[],
      draw :[],
      pieName: [],
      pieChart_1: null,
    }
  },
  methods: {
    getdata() {
      this.$axios.get("/api/family").then((res) => {
        console.log(res.data);
        if (res.data.status == 200) {
          this.tableData_out = res.data.tabledata;
        }
      })
    },
    statistics(){
      this.$axios.get("/api/draw").then((res) => {
        console.log(res.data);
        if (res.data.status == 200) {
          this.draw = res.data.tabledata;
        }
      });
      this.dialog_statistics = true;
      this.$axios.get("/api/statistics").then((res) => {
        console.log(res.data);
        if (res.data.status == 200) {
          this.tableData_statistics = res.data.tabledata;
          this.updatePieChart();
        }
      });
    },

    updatePieChart() {
      
      if (this.pieChart_1) {
        this.pieChart_1.destroy(); // 如果已存在饼图，先销毁
      }

      const ctx = document.getElementById('myPieChart').getContext('2d');
      const data = this.draw.map(item => item.TotalCoverage);
      const labels = this.draw.map(item => item.Name);

      this.pieChart_1 = new Chart(ctx, {
        type: 'pie',
        data: {
          labels: labels,
          datasets: [{
            data: data,
            backgroundColor: [
              '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40'
            ],
            hoverBackgroundColor: [
              '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40'
            ]
          }]
        },
        options: {
          responsive: true,
          plugins: {
            legend: {
              display: false
            },
            title: {
              display: true,
              text: '总保额',
              font: {
                size: 24
              }
            }
          }
        }
      });
    },

    showadd(){
      this.dialog_add = true;
    },


    add(){
      this.$axios.post("/api/addfamilymember", this.form_add).then((res) => {
        console.log(res.data);
        if (res.data.status == 200) {
          this.$message({
            message: "成功添加",
            type: "success"
          })
          this.dialog_add = false;
          this.getdata();
        }
      })
    },
    del(row){
      this.delete_id = row.IDNumber;
      this.$axios.delete("/api/family", { data: { delete_id: this.delete_id } }).then((res) => {
        console.log(res.data);
        if (res.data.status == 200) {
          this.$message({
            message: res.data.msg,
            type: "success"
          })
          this.getdata()
        }
      })
    },
  },

}

</script>



<style scoped>

</style>