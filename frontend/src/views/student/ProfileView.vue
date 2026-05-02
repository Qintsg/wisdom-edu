<template>
  <div class="profile-view">
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="15" animated />
    </div>

    <template v-else>
      <!-- Empty state appears only when the student has not produced any usable profile signals yet. -->
      <div v-if="noAssessmentDone" class="assessment-empty-card">
        <div class="empty-orbit" aria-hidden="true" />
        <div>
          <p class="empty-eyebrow">Profile signals needed</p>
          <h3>完成初始测评后，画像会变得可解释</h3>
          <p>系统会结合能力测评、知识测评和学习轨迹生成画像，而不是只展示静态标签。</p>
        </div>
        <el-button type="primary" @click="$router.push('/student/assessment')">
          前往测评中心
        </el-button>
      </div>

      <!-- Header collects identity, learner tags, and the manual refresh entry point. -->
      <section class="profile-hero">
        <div class="hero-ambient" aria-hidden="true" />
        <div class="hero-main">
          <el-avatar :size="86" class="user-avatar">
            {{ username.charAt(0).toUpperCase() }}
          </el-avatar>
          <div class="user-info">
            <p class="hero-eyebrow">Learner Profile</p>
            <h2>{{ username }} 的学习画像</h2>
            <p>基于学习数据、评测结果与知识追踪生成的个性化画像。</p>
            <div class="tags">
              <el-tag v-for="tag in learnerTags" :key="tag" effect="plain">{{ tag }}</el-tag>
              <el-tag v-if="!learnerTags.length" type="info" effect="plain">等待更多学习信号</el-tag>
            </div>
          </div>
        </div>
        <div class="hero-side">
          <div class="profile-score-card">
            <span>画像完整度</span>
            <strong>{{ profileCompleteness }}%</strong>
            <el-progress :percentage="profileCompleteness" :stroke-width="8" :show-text="false" />
          </div>
          <el-button :icon="Refresh" type="primary" class="refresh-btn" :loading="refreshing" @click="refreshProfile">
            刷新画像
          </el-button>
        </div>
      </section>

      <div class="metric-strip">
        <div class="metric-card">
          <span>能力均分</span>
          <strong>{{ abilityAverage }}%</strong>
          <em>{{ strongestAbility?.name || '暂无能力数据' }}</em>
        </div>
        <div class="metric-card">
          <span>掌握均值</span>
          <strong>{{ masteryAverage }}%</strong>
          <em>{{ learningFocusLabel }}</em>
        </div>
        <div class="metric-card accent">
          <span>AI 建议</span>
          <strong>{{ aiSuggestions.length }}</strong>
          <em>{{ assessmentReady ? '可持续刷新' : '完成测评后生成' }}</em>
        </div>
      </div>

      <div class="profile-overview-grid">
        <!-- Ability radar prefers the compact chart because dimensions are fixed and comparable. -->
        <el-card class="ability-card" shadow="hover">
          <template #header>
            <div class="card-header stacked">
              <div>
                <span class="card-eyebrow">Ability radar</span>
                <strong>能力画像</strong>
              </div>
              <el-tag v-if="abilityData.length" type="success" effect="plain">{{ abilityData.length }} 项能力</el-tag>
            </div>
          </template>
          <div v-if="abilityData.length" class="ability-chart-wrapper">
            <RadarChart :data="abilityData" :max="100" height="270px" color="#6d927d" :show-value="true" />
          </div>
          <div v-if="abilityData.length" class="ability-insights">
            <div class="insight-pill strong">
              <span>优势能力</span>
              <strong>{{ strongestAbility?.name }}</strong>
              <em>{{ strongestAbility?.value }}%</em>
            </div>
            <div class="insight-pill focus">
              <span>优先提升</span>
              <strong>{{ weakestAbility?.name }}</strong>
              <em>{{ weakestAbility?.value }}%</em>
            </div>
          </div>
          <div v-else class="chart-placeholder">
            <el-icon>
              <DataAnalysis />
            </el-icon>
            <p>暂无能力数据，请先完成能力测评。</p>
            <el-button type="primary" size="small" @click="$router.push('/student/assessment/ability')">
              前往能力测评
            </el-button>
          </div>
        </el-card>

        <!-- Mastery area uses a scroll container so long knowledge lists keep readable labels. -->
        <el-card class="mastery-card" shadow="hover">
          <template #header>
            <div class="card-header stacked">
              <div>
                <span class="card-eyebrow">Knowledge map</span>
                <strong>知识掌握度</strong>
              </div>
              <span class="mastery-meta">{{ masteryData.length }} 个知识点</span>
            </div>
          </template>

          <div v-if="masteryData.length" class="mastery-panel">
            <div class="mastery-pulse">
              <div>
                <span>整体掌握均值</span>
                <strong>{{ masteryAverage }}%</strong>
              </div>
              <el-progress :percentage="masteryAverage" :stroke-width="12" :show-text="false" />
            </div>

            <div class="mastery-summary">
              <div class="mastery-stat">
                <strong>{{ highMasteryCount }}</strong>
                <span>高掌握</span>
              </div>
              <div class="mastery-stat">
                <strong>{{ mediumMasteryCount }}</strong>
                <span>待巩固</span>
              </div>
              <div class="mastery-stat warning">
                <strong>{{ lowMasteryCount }}</strong>
                <span>薄弱项</span>
              </div>
            </div>

            <div v-if="topWeakMasteries.length" class="focus-cluster">
              <span>优先突破</span>
              <el-tag v-for="item in topWeakMasteries" :key="item.pointId || item.name" type="warning" effect="plain">
                {{ item.name }} · {{ item.value }}%
              </el-tag>
            </div>

            <div class="mastery-chart-scroller" :style="{ maxHeight: masteryViewportHeight + 'px' }">
              <div ref="masteryChartRef" :style="{ height: masteryChartHeight + 'px', width: '100%' }"></div>
            </div>
          </div>

          <div v-else class="chart-placeholder">
            <el-icon>
              <DataAnalysis />
            </el-icon>
            <p>暂无知识数据，请先完成知识测评。</p>
            <el-button type="primary" size="small" @click="$router.push('/student/assessment/knowledge')">
              前往知识测评
            </el-button>
          </div>
        </el-card>
      </div>

      <!-- Summary text is optional because some courses only return structured chart data. -->
      <el-card v-if="profileSummary || profileWeakness || profileStrength" class="summary-card" shadow="hover">
        <template #header>
          <div class="card-header stacked">
            <div>
              <span class="card-eyebrow">Interpretation</span>
              <strong>画像总结</strong>
            </div>
          </div>
        </template>
        <div class="summary-layout" :class="{ 'single-summary': !(profileStrength || profileWeakness) }">
          <p v-if="profileSummary" class="summary-text">{{ profileSummary }}</p>
          <div v-if="profileStrength || profileWeakness" class="summary-lenses">
            <div v-if="profileStrength" class="summary-block strength-block">
              <el-tag type="success" effect="plain" size="small">学习优势</el-tag>
              <p class="summary-strength">{{ profileStrength }}</p>
            </div>
            <div v-if="profileWeakness" class="summary-block weakness-block">
              <el-tag type="warning" effect="plain" size="small">薄弱环节</el-tag>
              <p class="summary-weakness">{{ profileWeakness }}</p>
            </div>
          </div>
        </div>
      </el-card>

      <!-- AI advice is intentionally isolated from the base profile so stale suggestions can retry safely. -->
      <el-card class="ai-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon>
                <MagicStick />
              </el-icon> AI 学习建议</span>
            <el-button v-if="assessmentReady" :icon="Refresh" text :loading="aiLoading" @click="refreshAISuggestions">
              刷新 AI 建议
            </el-button>
          </div>
        </template>
        <div v-if="!assessmentReady" class="chart-placeholder ai-placeholder">
          <el-icon>
            <DataAnalysis />
          </el-icon>
          <p>请先完成初始测评，系统才会生成 AI 学习建议。</p>
          <el-button type="primary" size="small" @click="$router.push('/student/assessment')">
            前往测评中心
          </el-button>
        </div>
        <div v-else-if="aiLoading" class="ai-loading">
          <el-progress :percentage="aiProgressPercent" :stroke-width="10" :show-text="true" status="" />
          <p class="ai-progress-stage">{{ aiProgressStageText }}</p>
        </div>
        <div v-else class="ai-content">
          <template v-if="aiLoadFailed">
            <el-alert type="warning" :closable="false" title="获取 AI 学习建议失败" show-icon />
            <div class="retry-row">
              <el-button type="primary" size="small" @click="loadAISuggestions">
                重新获取
              </el-button>
            </div>
          </template>
          <template v-else>
            <!-- Suggestions are rendered as a merged flat list because the API may split them across fields. -->
            <p class="ai-lead">系统基于当前画像，推荐以下学习动作：</p>
            <div v-if="aiSuggestions.length" class="suggestion-grid">
              <article v-for="(suggestion, index) in aiSuggestions" :key="index" class="suggestion-card">
                <span>{{ String(index + 1).padStart(2, '0') }}</span>
                <p>{{ suggestion }}</p>
              </article>
            </div>
            <el-empty v-if="!aiSuggestions.length" description="暂无学习建议" />
          </template>
        </div>
      </el-card>
    </template>
  </div>
</template>

<script setup>
import { DataAnalysis, MagicStick, Refresh } from '@element-plus/icons-vue'
import RadarChart from '@/components/charts/RadarChart.vue'
import { useProfileView } from './useProfileView'

const {
  abilityAverage,
  abilityData,
  aiLoadFailed,
  aiLoading,
  aiProgressPercent,
  aiProgressStageText,
  aiSuggestions,
  assessmentReady,
  highMasteryCount,
  learnerTags,
  learningFocusLabel,
  loadAISuggestions,
  loading,
  lowMasteryCount,
  masteryAverage,
  masteryChartHeight,
  masteryChartRef,
  masteryData,
  masteryViewportHeight,
  mediumMasteryCount,
  noAssessmentDone,
  profileCompleteness,
  profileStrength,
  profileSummary,
  profileWeakness,
  refreshAISuggestions,
  refreshing,
  refreshProfile,
  strongestAbility,
  topWeakMasteries,
  username,
  weakestAbility
} = useProfileView()
</script>

<style scoped src="./ProfileView.css"></style>
<style scoped src="./ProfileViewPanels.css"></style>
