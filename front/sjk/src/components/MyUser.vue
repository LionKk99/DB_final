<template>
    <div>
        <div class="body">
            <!-- 左侧导航栏 -->
            <div class="liner">
                <div style="height:80px;color:white;display:flex;align-items:center;justify-content:center">
                  <img src="@/assets/guanjia.png" alt="" style="width:60px;height:60px">
                  <span style="margin-left:5px;font-size:24px">家庭保单小管家</span>
                </div>


                <el-menu default-active="1" class="el-menu-vertical-demo" background-color="#001529" text-color="rgba(255,255,255,0.65)"
                         active-text-color="#fff" @select="handleselect">
                    <el-menu-item index="1">
                      家庭保单
                    </el-menu-item>
                    <el-menu-item index="2">
                      家庭成员
                    </el-menu-item>
                    <el-menu-item index="3">
                      理赔记录
                    </el-menu-item>
                    <el-menu-item index="4">
                      推荐系统
                    </el-menu-item>
                </el-menu>

            </div>


            <div class="main">
                <div id="FamilyIn" v-show="active == 1">
                    <FamilyIn></FamilyIn>
                </div>

                <div id="FamilyMe" v-show="active == 2">
                    <FamilyMe></FamilyMe>
                </div>

                <div id="LiPei" v-show="active == 3">
                    <LiPei></LiPei>
                </div>

                <div id="RecSys" v-show="active == 4">
                  <RecSys></RecSys>
                </div>
            </div>

        </div>

    </div>
</template>

<script>
import FamilyIn from '@/components/FamilyIn.vue'
import FamilyMe from '@/components/FamilyMe.vue'
import LiPei from '@/components/LiPei.vue'
import RecSys from '@/components/RecSys.vue'
export default {
    components: {
        FamilyIn: FamilyIn,
        FamilyMe: FamilyMe,
        LiPei: LiPei,
        RecSys:RecSys,
    },
    data() {
        return {
            active: 1,
        };
    },
    methods: {
        handleselect(index) {
            this.active = index;
        }
    },
}  
</script>

<style scoped>
.el-menu-item:hover{
  color:#fff !important
}
.el-menu-item.is-active{
  background-color: #1890ff !important;
  border-radius: 5px !important;
  margin: 4px !important
}
.el-menu-item{
  height:80px !important;
  line-height:80px !important;
  margin: 4px !important;
  font-size:20px !important
}
.el-dropdown-link {
  cursor: pointer;
  color: #409EFF;
}
.el-icon-arrow-down {
  font-size: 12px;
}
.body {
  width: 100%;
  height: 1600px;
  display: flex;
  justify-content: space-around;
}
.liner {
  width: 15%;
  height: 100%;
  background-color:#001529;
}
.main {
  width: 85%;
}
</style>