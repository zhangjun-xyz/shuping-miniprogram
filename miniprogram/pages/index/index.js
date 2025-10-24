//index.js
const app = getApp()

Page({
  data: {
    isLoading: false,
    loadingText: '处理中...'
  },

  onLoad: function() {
    console.log('首页加载完成')
  },

  // 拍照并自动识别
  takePhotoAndRecognize: function() {
    const that = this
    wx.chooseMedia({
      count: 1,
      mediaType: ['image'],
      sourceType: ['camera'],
      camera: 'back',
      success: function(res) {
        const imageUrl = res.tempFiles[0].tempFilePath
        // 拍照成功后立即识别
        that.recognizeBookImage(imageUrl)
      },
      fail: function(error) {
        console.error('拍照失败:', error)
        wx.showToast({
          title: '拍照失败，请重试',
          icon: 'none'
        })
      }
    })
  },

  // 从相册选择并自动识别
  chooseImageAndRecognize: function() {
    const that = this
    wx.chooseMedia({
      count: 1,
      mediaType: ['image'],
      sourceType: ['album'],
      success: function(res) {
        const imageUrl = res.tempFiles[0].tempFilePath
        // 选择成功后立即识别
        that.recognizeBookImage(imageUrl)
      },
      fail: function(error) {
        console.error('选择图片失败:', error)
        wx.showToast({
          title: '选择图片失败，请重试',
          icon: 'none'
        })
      }
    })
  },

  // 识别书籍图片
  recognizeBookImage: function(imageUrl) {
    if (!imageUrl) {
      wx.showToast({
        title: '图片无效，请重试',
        icon: 'none'
      })
      return
    }

    this.setData({
      isLoading: true,
      loadingText: '正在识别书籍...'
    })

    // 上传图片到服务器并识别
    this.uploadImageAndRecognize(imageUrl)
  },

  // 上传图片并识别
  uploadImageAndRecognize: function(imageUrl) {
    const that = this

    wx.uploadFile({
      url: `${app.globalData.apiBaseUrl}/api/recognize-book`,
      filePath: imageUrl,
      name: 'image',
      timeout: 60000, // 60秒超时
      header: {
        'content-type': 'multipart/form-data'
      },
      success: function(res) {
        try {
          const data = JSON.parse(res.data)
          that.handleRecognitionResult(data)
        } catch (error) {
          console.error('解析响应失败:', error)
          that.showError('服务器响应格式错误')
        }
      },
      fail: function(error) {
        console.error('上传失败:', error)
        that.showError('上传失败，请检查网络连接')
      },
      complete: function() {
        that.setData({
          isLoading: false
        })
      }
    })
  },

  // 处理识别结果
  handleRecognitionResult: function(data) {
    if (data.success) {
      // 跳转到结果页面
      wx.navigateTo({
        url: `/pages/result/result?data=${encodeURIComponent(JSON.stringify(data.data))}`
      })
    } else {
      this.showError(data.error || '识别失败')
    }
  },

  // 显示错误信息
  showError: function(message) {
    wx.showModal({
      title: '提示',
      content: message,
      showCancel: false,
      confirmText: '知道了'
    })
  }
})
