<template>
    <div>
      <el-header>
        <div style="text-align: center;">
          <h1>理赔记录</h1>
        </div>
      </el-header>
      <el-main>


        <el-row :gutter="20">
          <el-button type="primary" @click="showadd()">添加</el-button>
        </el-row>

        <el-dialog title="添加保单" :visible.sync="dialog_add" width="40%" center>
          <div>
            <el-form ref="form" :model="form_add" label-width="100px">

              <el-form-item label="理赔单号：">
                <el-input v-model="form_add.ClaimNumber"></el-input>
              </el-form-item>

              <el-form-item label="保单号：">
                <el-input v-model="form_add.PolicyID"></el-input>
              </el-form-item>

              <el-form-item label="理赔金额：">
                <el-input v-model="form_add.ClaimAmount"></el-input>
              </el-form-item>

              <el-form-item label="理赔时间：">
                <el-input v-model="form_add.ClaimTime"></el-input>
              </el-form-item>

              <el-form-item label="理赔原因：">
                <el-input v-model="form_add.Reason"></el-input>
              </el-form-item>


            </el-form>

            <div style="text-align: center;">
              <el-button type="primary" @click="add()">
                提交
              </el-button>
            </div>

          </div>
        </el-dialog>

        <el-table :data="tableData" style="width: 100%">
          <el-table-column prop="ClaimNumber" label="理赔单号" width="380" align="center"></el-table-column>
          <el-table-column prop="PolicyID" label="保单号" width="380" align="center"></el-table-column>
          <el-table-column prop="ClaimAmount" label="理赔金额" width="380" align="center"></el-table-column>
          <el-table-column prop="ClaimTime" label="理赔时间" width="380" align="center"></el-table-column>
          <el-table-column prop="Reason" label="理赔原因" width="380" align="center"></el-table-column>
          <el-table-column prop="operate" label="操作" align="center" >
            <template slot-scope="scope">
              <el-button type="danger" @click="del(scope.row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>

      </el-main>
    </div>
</template>

<script>
export default {
  created() {
    this.getdata();
  },
  data() {
    return {
      tableData: [],
      dialog_add: false,
      form_add:{
        ClaimNumber:'',
        PolicyID:'',
        ClaimAmount:'',
        ClaimTime:'',
        Reason:'',
      },
    }
  },
  methods: {
    getdata() {
      this.$axios.get("/api/claimsrecord").then((res) => {
        console.log(res.data);
        if (res.data.status == 200) {
          this.tableData = res.data.tabledata;
        }
      })
    },
    showadd(){
      this.dialog_add = true
    },
    add(){
      this.$axios.post("/api/addclaim", this.form_add).then((res) => {
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
      this.delete_id = row.ClaimNumber;
      this.$axios.delete("/api/claimsrecord", { data: { delete_id: this.delete_id } }).then((res) => {
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
  }
}
</script>

<style scoped>

</style>