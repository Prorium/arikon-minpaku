import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Label } from '@/components/ui/label.jsx'
import { Slider } from '@/components/ui/slider.jsx'
import { Checkbox } from '@/components/ui/checkbox.jsx'
import { Home, MapPin, Calculator, TrendingUp, Users, Building, Zap, ExternalLink, QrCode, CheckCircle } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts'
import LineIntegrationSimple from './components/LineIntegrationSimple';
import UserIdentificationSystem from './components/UserIdentificationSystem';
import './components/LMessageIntegration.css';
import './utils/canvasPolyfill.js';
import './App.css'

// データインポート
import regionData from '../data/region_data.json'
import propertyData from '../data/property_types.json'

function App() {
  const [currentStep, setCurrentStep] = useState(0)
  const [formData, setFormData] = useState({
    region: '',
    propertyType: '',
    monthlyRent: 100000,
    furnitureAppliances: true,
    renovationCost: 0,
    managementFeeRate: 10,
    cleaningFee: 0
  })
  const [results, setResults] = useState(null)
  const [isCalculating, setIsCalculating] = useState(false)
  const [showLineInfo, setShowLineInfo] = useState(false);
  const [showLMessage, setShowLMessage] = useState(false);
  const [showUserIdentification, setShowUserIdentification] = useState(false);
  const steps = [
    { title: 'ランディング', icon: Home },
    { title: '地域選択', icon: MapPin },
    { title: '物件タイプ', icon: Building },
    { title: '家賃・費用', icon: Calculator },
    { title: '追加オプション', icon: Zap },
    { title: '結果表示', icon: TrendingUp }
  ]

  const regions = [
    { value: '東京都', label: '東京都', description: '活気ある首都', avgRate: '70%', avgPrice: '¥25,000' },
    { value: '大阪府', label: '大阪府', description: '関西の中心地', avgRate: '68%', avgPrice: '¥20,000' },
    { value: '京都府', label: '京都府', description: '歴史的な観光地', avgRate: '65%', avgPrice: '¥22,000' },
    { value: '福岡県', label: '福岡県', description: '九州の玄関口', avgRate: '60%', avgPrice: '¥18,000' },
    { value: '沖縄県', label: '沖縄県', description: 'リゾート地', avgRate: '62%', avgPrice: '¥20,000' },
    { value: '北海道', label: '北海道', description: '自然豊かな観光地', avgRate: '55%', avgPrice: '¥15,000' },
    { value: 'その他地方', label: 'その他地方', description: '地方都市', avgRate: '40%', avgPrice: '¥10,000' }
  ]

  const propertyTypes = [
    { value: '1K', label: '1K', maxOccupancy: 2, icon: '🏠' },
    { value: '1DK', label: '1DK', maxOccupancy: 2, icon: '🏠' },
    { value: '1LDK', label: '1LDK', maxOccupancy: 3, icon: '🏡' },
    { value: '2LDK', label: '2LDK', maxOccupancy: 4, icon: '🏡' },
    { value: '3LDK', label: '3LDK', maxOccupancy: 6, icon: '🏘️' },
    { value: '戸建て', label: '戸建て', maxOccupancy: 8, icon: '🏘️' }
  ]

  const calculateResults = async () => {
    setIsCalculating(true)
    
    try {
      const response = await fetch('/api/simulation/calculate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        const data = await response.json();
        setResults(data);
        setCurrentStep(5);
      } else {
        console.error('Calculation failed');
        alert('計算に失敗しました。もう一度お試しください。');
      }
    } catch (error) {
      console.error('Error calculating results:', error);
      alert('エラーが発生しました。もう一度お試しください。');
    } finally {
      setIsCalculating(false);
    }
  };

  const nextStep = () => {
    if (currentStep === 4) {
      calculateResults()
    } else {
      setCurrentStep(prev => Math.min(prev + 1, steps.length - 1))
    }
  }

  const prevStep = () => {
    setCurrentStep(prev => Math.max(prev - 1, 0))
  }

  const renderLandingPage = () => (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50 flex items-center justify-center p-4">
      <div className="max-w-4xl mx-auto text-center">
        <div className="mb-8">
          <div className="flex items-center justify-center mb-4">
            <img 
              src="/data.png" 
              alt="有村晃の民泊塾" 
              className="h-16 md:h-20 object-contain"
            />
          </div>
        </div>
        
        <h2 className="text-5xl font-bold text-gray-800 mb-4">
          3分で分かる！<br />
          あなたの民泊投資収益
        </h2>
        
        <p className="text-xl text-gray-600 mb-8">
          あなたの民泊投資にすべて答える
        </p>
        
        <Button 
          onClick={nextStep}
          className="bg-green-500 hover:bg-green-600 text-white px-8 py-4 text-lg rounded-full mb-12"
        >
          シミュレーションを始める
        </Button>
        
        <div className="grid md:grid-cols-3 gap-8 mt-12">
          <Card className="bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Zap className="w-8 h-8 text-blue-600" />
              </div>
              <CardTitle>ゲーム感覚の算出</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">楽しくシミュレーション</p>
            </CardContent>
          </Card>
          
          <Card className="bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Calculator className="w-8 h-8 text-green-600" />
              </div>
              <CardTitle>簡単な入力</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">必要なデータにサポート</p>
            </CardContent>
          </Card>
          
          <Card className="bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <TrendingUp className="w-8 h-8 text-purple-600" />
              </div>
              <CardTitle>詳細な分析</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">収益性の詳細分析</p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )

  const renderRegionSelection = () => (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50 p-4">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-800 mb-4">地域を選択</h2>
          <div className="flex items-center mb-4">
            <span className="text-sm text-gray-600 mr-4">Step 1 of 5</span>
            <Progress value={20} className="flex-1" />
          </div>
        </div>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {regions.map((region) => (
            <Card 
              key={region.value}
              className={`cursor-pointer transition-all hover:shadow-lg ${
                formData.region === region.value ? 'ring-2 ring-blue-500 bg-blue-50' : 'bg-white'
              }`}
              onClick={() => setFormData(prev => ({ ...prev, region: region.value }))}
            >
              <CardHeader>
                <CardTitle className="flex items-center">
                  <MapPin className="w-5 h-5 mr-2 text-blue-600" />
                  {region.label}
                </CardTitle>
                <CardDescription>{region.description}</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">平均稼働率</span>
                    <span className="text-sm font-medium">{region.avgRate}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">平均単価</span>
                    <span className="text-sm font-medium">{region.avgPrice}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
        
        <div className="flex justify-between mt-8">
          <Button onClick={prevStep} variant="outline">戻る</Button>
          <Button 
            onClick={nextStep} 
            disabled={!formData.region}
            className="bg-blue-600 hover:bg-blue-700"
          >
            次へ
          </Button>
        </div>
      </div>
    </div>
  )

  const renderPropertyTypeSelection = () => (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50 p-4">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-800 mb-4">物件タイプを選択</h2>
          <div className="flex items-center mb-4">
            <span className="text-sm text-gray-600 mr-4">Step 2 of 5</span>
            <Progress value={40} className="flex-1" />
          </div>
        </div>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {propertyTypes.map((property) => (
            <Card 
              key={property.value}
              className={`cursor-pointer transition-all hover:shadow-lg ${
                formData.propertyType === property.value ? 'ring-2 ring-blue-500 bg-blue-50' : 'bg-white'
              }`}
              onClick={() => setFormData(prev => ({ ...prev, propertyType: property.value }))}
            >
              <CardHeader className="text-center">
                <div className="text-4xl mb-2">{property.icon}</div>
                <CardTitle>{property.label}</CardTitle>
                <CardDescription>
                  <Users className="w-4 h-4 inline mr-1" />
                  最大{property.maxOccupancy}名まで
                </CardDescription>
              </CardHeader>
            </Card>
          ))}
        </div>
        
        <div className="flex justify-between mt-8">
          <Button onClick={prevStep} variant="outline">戻る</Button>
          <Button 
            onClick={nextStep} 
            disabled={!formData.propertyType}
            className="bg-blue-600 hover:bg-blue-700"
          >
            次へ
          </Button>
        </div>
      </div>
    </div>
  )

  const renderRentInput = () => (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50 p-4">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-800 mb-4">家賃・初期費用</h2>
          <div className="flex items-center mb-4">
            <span className="text-sm text-gray-600 mr-4">Step 3 of 5</span>
            <Progress value={60} className="flex-1" />
          </div>
        </div>
        
        <Card className="bg-white">
          <CardHeader>
            <CardTitle>月額家賃</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div>
              <Label htmlFor="rent">月額家賃 (円)</Label>
              <div className="mt-2">
                <Slider
                  value={[formData.monthlyRent]}
                  onValueChange={(value) => setFormData(prev => ({ ...prev, monthlyRent: value[0] }))}
                  max={500000}
                  min={30000}
                  step={10000}
                  className="mb-4"
                />
                <Input
                  id="rent"
                  type="number"
                  value={formData.monthlyRent}
                  onChange={(e) => setFormData(prev => ({ ...prev, monthlyRent: parseInt(e.target.value) || 0 }))}
                  className="text-center text-lg font-bold"
                />
              </div>
            </div>
            
            {formData.propertyType && (
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="font-semibold mb-3">自動計算される初期費用</h3>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>敷金・礼金・仲介手数料</span>
                    <span className="font-medium">
                      ¥{(formData.monthlyRent * propertyData[formData.propertyType].初期費用倍率).toLocaleString()}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>月額清掃費</span>
                    <span className="font-medium">
                      ¥{propertyData[formData.propertyType].月額清掃費.toLocaleString()}
                    </span>
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
        
        <div className="flex justify-between mt-8">
          <Button onClick={prevStep} variant="outline">戻る</Button>
          <Button 
            onClick={nextStep}
            className="bg-blue-600 hover:bg-blue-700"
          >
            次へ
          </Button>
        </div>
      </div>
    </div>
  )

  const renderOptionsInput = () => (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50 p-4">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-800 mb-4">追加オプション</h2>
          <div className="flex items-center mb-4">
            <span className="text-sm text-gray-600 mr-4">Step 4 of 5</span>
            <Progress value={80} className="flex-1" />
          </div>
        </div>
        
        <div className="space-y-6">
          <Card className="bg-white">
            <CardHeader>
              <CardTitle>家具・家電</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="furniture"
                  checked={formData.furnitureAppliances}
                  onCheckedChange={(checked) => setFormData(prev => ({ ...prev, furnitureAppliances: checked }))}
                />
                <Label htmlFor="furniture">
                  家具・家電を購入する 
                  {formData.propertyType && (
                    <span className="text-gray-600 ml-2">
                      (¥{propertyData[formData.propertyType].家具家電費.toLocaleString()})
                    </span>
                  )}
                </Label>
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-white">
            <CardHeader>
              <CardTitle>リフォーム費用</CardTitle>
            </CardHeader>
            <CardContent>
              <Label htmlFor="renovation">リフォーム費用 (円)</Label>
              <div className="mt-2">
                <Slider
                  value={[formData.renovationCost]}
                  onValueChange={(value) => setFormData(prev => ({ ...prev, renovationCost: value[0] }))}
                  max={2000000}
                  min={0}
                  step={50000}
                  className="mb-4"
                />
                <Input
                  id="renovation"
                  type="number"
                  value={formData.renovationCost}
                  onChange={(e) => setFormData(prev => ({ ...prev, renovationCost: parseInt(e.target.value) || 0 }))}
                  className="text-center"
                />
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-white">
            <CardHeader>
              <CardTitle>運営代行費</CardTitle>
            </CardHeader>
            <CardContent>
              <Label htmlFor="management">売上に対する運営代行費 (%)</Label>
              <div className="mt-2">
                <Slider
                  value={[formData.managementFeeRate]}
                  onValueChange={(value) => setFormData(prev => ({ ...prev, managementFeeRate: value[0] }))}
                  max={30}
                  min={0}
                  step={1}
                  className="mb-4"
                />
                <Input
                  id="management"
                  type="number"
                  value={formData.managementFeeRate}
                  onChange={(e) => setFormData(prev => ({ ...prev, managementFeeRate: parseInt(e.target.value) || 0 }))}
                  className="text-center"
                />
              </div>
            </CardContent>
          </Card>
        </div>
        
        <div className="flex justify-between mt-8">
          <Button onClick={prevStep} variant="outline">戻る</Button>
          <Button 
            onClick={nextStep}
            disabled={isCalculating}
            className="bg-blue-600 hover:bg-blue-700"
          >
            {isCalculating ? '計算中...' : '結果を計算'}
          </Button>
        </div>
      </div>
    </div>
  )

  const renderResults = () => (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50 p-4">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-800 mb-4">計算完了！</h2>
          <div className="flex items-center mb-4">
            <span className="text-sm text-gray-600 mr-4">Step 5 of 5</span>
            <Progress value={100} className="flex-1" />
          </div>
          
          {/* 最上部のLINEボタン */}
          <div className="text-center mb-6">
            <button 
              className="cta-button text-xl py-4 px-8 bg-green-500 hover:bg-green-600 text-white rounded-full"
              onClick={() => setShowUserIdentification(true)}
            >
              📱 LINEで結果を受け取る
            </button>
          </div>
        </div>
        
        {results && (
          <div className="space-y-6">
            {/* LINE登録案内 */}
            <Card className="bg-gradient-to-r from-green-500 to-blue-600 text-white">
              <CardHeader>
                <CardTitle className="text-center text-3xl">🎉 シミュレーション完了！</CardTitle>
                <CardDescription className="text-center text-green-100 text-lg">
                  詳細な分析結果をLINEでお送りします
                </CardDescription>
              </CardHeader>
              <CardContent className="text-center space-y-6">
                {/* LINEボタンを最上部に配置 */}
                <div className="result-actions mb-8">
                  <button 
                    className="cta-button text-xl py-4 px-8"
                    onClick={() => setShowUserIdentification(true)}
                  >
                    📱 LINE友だち追加で結果を受け取る
                  </button>
                </div>
                
                <div className="mb-6 p-6 bg-white/10 rounded-lg border-2 border-dashed border-white/30">
                  <div className="text-6xl mb-4">📊</div>
                  <h3 className="text-2xl font-bold mb-4">LINE登録で受け取れる詳細分析</h3>
                  <p className="text-lg opacity-90">
                    年間売上・費用・利回り・回収期間など、投資判断に必要な全てのデータをお送りします
                  </p>
                </div>

                <div className="grid md:grid-cols-2 gap-4 text-sm mb-8">
                  <div className="bg-white/20 p-4 rounded-lg">
                    <h4 className="font-semibold mb-2">💰 基本収益情報</h4>
                    <p className="text-xs opacity-90">年間売上・費用・利益・利回り・回収期間</p>
                  </div>
                  <div className="bg-white/20 p-4 rounded-lg">
                    <h4 className="font-semibold mb-2">📈 月別収益推移</h4>
                    <p className="text-xs opacity-90">売上・費用・利益の詳細な月別推移</p>
                  </div>
                  <div className="bg-white/20 p-4 rounded-lg">
                    <h4 className="font-semibold mb-2">🗾 地域比較分析</h4>
                    <p className="text-xs opacity-90">他地域との収益性・稼働率比較</p>
                  </div>
                  <div className="bg-white/20 p-4 rounded-lg">
                    <h4 className="font-semibold mb-2">⚠️ リスク分析</h4>
                    <p className="text-xs opacity-90">投資リスクの詳細評価と対策</p>
                  </div>
                  <div className="bg-white/20 p-4 rounded-lg">
                    <h4 className="font-semibold mb-2">💡 改善提案</h4>
                    <p className="text-xs opacity-90">収益向上の具体的な改善案</p>
                  </div>
                  <div className="bg-white/20 p-4 rounded-lg">
                    <h4 className="font-semibold mb-2">🎓 民泊塾特別案内</h4>
                    <p className="text-xs opacity-90">LINE限定50%OFFでのスクール案内</p>
                  </div>
                </div>
                
                <p className="text-sm text-green-100">
                  ※登録は無料です。友だち追加後、自動で詳細な分析結果をお送りします。
                </p>
              </CardContent>
            </Card>

      {/* ユーザー識別システム */}
      {showUserIdentification && (
        <UserIdentificationSystem 
          simulationResult={results}
          onClose={() => setShowUserIdentification(false)}
        />
      )}

      {/* エルメール連携（旧版） */}
      {showLMessage && (
              <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
                <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
                  <div className="sticky top-0 bg-white border-b p-4 flex justify-between items-center">
                    <h2 className="text-xl font-bold">LINE自動応答設定</h2>
                    <button 
                      onClick={() => setShowLMessage(false)}
                      className="text-gray-500 hover:text-gray-700"
                    >
                      ✕
                    </button>
                  </div>
                  <div className="p-4">
                    <LMessageIntegration 
                      simulationResult={results}
                      onComplete={() => setShowLMessage(false)}
                    />
                  </div>
                </div>
              </div>
            )}

            {/* LINE登録情報 */}
            {showLineInfo && (
              <LineIntegrationSimple 
                simulationResults={results}
                onClose={() => setShowLineInfo(false)}
              />
            )}
            
            {/* 免責事項 */}
            <Card className="bg-yellow-50 border-yellow-200">
              <CardContent className="pt-6">
                <p className="text-sm text-yellow-800">
                  <strong>免責事項：</strong>
                  このシミュレーション結果は参考値であり、実際の投資収益を保証するものではありません。
                  投資判断は自己責任で行ってください。
                </p>
              </CardContent>
            </Card>
          </div>
        )}
        
        <div className="flex justify-between mt-8">
          <Button 
            onClick={() => {
              setCurrentStep(0)
              setFormData({
                region: '',
                propertyType: '',
                monthlyRent: 100000,
                furnitureAppliances: true,
                renovationCost: 0,
                managementFeeRate: 10,
                cleaningFee: 0
              })
              setResults(null)
              setShowLineInfo(false);
              setShowLMessage(false);
              setShowUserIdentification(false);
              setShowImageGenerator(false);
            }}
            variant="outline"
          >
            新しいシミュレーション
          </Button>
        </div>
      </div>
      
    </div>
  )

  const renderStep = () => {
    switch (currentStep) {
      case 0: return renderLandingPage()
      case 1: return renderRegionSelection()
      case 2: return renderPropertyTypeSelection()
      case 3: return renderRentInput()
      case 4: return renderOptionsInput()
      case 5: return renderResults()
      default: return renderLandingPage()
    }
  }

  return (
    <div className="min-h-screen">
      {renderStep()}
      
      {/* フッター */}
<footer className="bg-gray-800 text-white py-8">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <div className="mb-4">
            <img 
              src="/data_mark.png" 
              alt="有村晃の民泊塾" 
              className="h-8 w-8 mx-auto mb-2 opacity-80"
            />
          </div>
          <p className="mb-2">運営会社：株式会社Prorium</p>

        </div>
      </footer>
    </div>
  )
}

export default App

