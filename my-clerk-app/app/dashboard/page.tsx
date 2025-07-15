'use client'

import { useAuth, useUser } from '@clerk/nextjs'
import { useEffect, useState, useCallback } from 'react'
import Link from 'next/link'
import Image from 'next/image'
import { motion, AnimatePresence } from 'framer-motion'

export default function Dashboard() {
  const { getToken, isLoaded, userId } = useAuth()
  const { user } = useUser()
  const [streamlitUrl, setStreamlitUrl] = useState<string>('')
  const [isGeneratingUrl, setIsGeneratingUrl] = useState(false)
  const [showEmbedded, setShowEmbedded] = useState(false)
  const [activeTab, setActiveTab] = useState('overview')
  const [notifications, setNotifications] = useState<Array<{ id: number, message: string, type: 'success' | 'error' | 'info' }>>([])

  const addNotification = (message: string, type: 'success' | 'error' | 'info' = 'info') => {
    const id = Date.now()
    setNotifications(prev => [...prev, { id, message, type }])
    setTimeout(() => {
      setNotifications(prev => prev.filter(n => n.id !== id))
    }, 5000)
  }

  // Generate the Streamlit URL with JWT token
  const generateStreamlitUrl = useCallback(async () => {
    if (!isLoaded || !userId) return

    setIsGeneratingUrl(true)
    try {
      console.log('🔄 Generating fresh JWT token...')
      addNotification('Generating authentication token...', 'info')

      // Output user info for debugging
      if (user) {
        console.log('📝 User Info from Clerk:')
        console.log('- User ID:', user.id)
        console.log('- Username:', user.username)
        console.log('- Email:', user.primaryEmailAddress?.emailAddress)
        console.log('- Image URL:', user.imageUrl)
      }

      // Always get a fresh token to avoid expiration issues
      // Use the JWT template name we created in Clerk dashboard
      // Make sure this template in Clerk includes all necessary user data fields
      const token = await getToken({ template: "crawlmind_backend" })

      if (token) {
        console.log('✅ Fresh JWT Token generated successfully')
        console.log('🔍 Token length:', token.length)
        addNotification('Authentication token generated successfully!', 'success')

        // Decode token for verification
        try {
          const parts = token.split('.');
          if (parts.length > 1) {
            const payload = JSON.parse(atob(parts[1]));
            console.log('🔍 Token payload:', payload);
            console.log('- user_id:', payload.user_id);
            console.log('- username:', payload.username);
          }
        } catch (e) {
          console.error('Error decoding token:', e);
        }

        // Base Streamlit URL (update port if needed)
        const baseUrl = 'http://localhost:8501'

        // Add token as URL parameter with timestamp to force refresh
        const timestamp = Date.now()
        const urlWithToken = `${baseUrl}?token=${encodeURIComponent(token)}&t=${timestamp}`

        console.log('🔗 Generated Streamlit URL')
        setStreamlitUrl(urlWithToken)
      } else {
        console.error('❌ No token received from Clerk')
        addNotification('Failed to generate authentication token', 'error')
      }
    } catch (error) {
      console.error('❌ Error generating token:', error)
      addNotification('Error generating authentication token', 'error')
    } finally {
      setIsGeneratingUrl(false)
    }
  }, [isLoaded, userId, user, getToken])

  // Debugging function to display token details
  const debugToken = async () => {
    if (!isLoaded || !userId) return

    try {
      console.log('🔄 Generating token for debugging...')

      // Get a fresh token with template
      const token = await getToken({ template: "crawlmind_backend" })

      if (token) {
        console.log('✅ Token generated for debugging')

        // Display token parts
        const tokenParts = token.split('.')
        if (tokenParts.length === 3) {
          // Decode header and payload (not the signature)
          try {
            const header = JSON.parse(atob(tokenParts[0]))
            const payload = JSON.parse(atob(tokenParts[1]))

            console.log('🔍 Token Header:', header)
            console.log('🔍 Token Payload:', payload)
            console.log('🔍 Has "aud" claim:', Boolean(payload.aud))
            console.log('🔍 Audience value:', payload.aud)

            // Display in UI
            alert(
              `Token Debugging Info:\n` +
              `- Token Length: ${token.length}\n` +
              `- Has "aud" claim: ${Boolean(payload.aud)}\n` +
              `- Audience: ${payload.aud || 'Not set'}\n` +
              `- User ID: ${payload.user_id || 'Not found'}\n` +
              `- Username: ${payload.username || 'Not found'}\n` +
              `- Issuer: ${payload.iss || 'Not set'}\n` +
              `- Expiration: ${new Date(payload.exp * 1000).toLocaleString()}`
            )

          } catch (e) {
            console.error('❌ Error decoding token:', e)
            alert('Error decoding token. See console for details.')
          }
        }
      }
    } catch (error) {
      console.error('❌ Error debugging token:', error)
    }
  }

  // Generate URL when component mounts
  useEffect(() => {
    generateStreamlitUrl()
  }, [generateStreamlitUrl])

  if (!isLoaded) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: 'linear-gradient(135deg, #000000, #1a1a1a, #000000)' }}>
        <motion.div
          className="text-center"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
        >
          <motion.div
            className="animate-spin rounded-full h-16 w-16 mx-auto mb-6"
            style={{
              border: '4px solid rgba(74, 158, 255, 0.3)',
              borderTop: '4px solid #4A9EFF'
            }}
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          />
          <motion.h2
            className="text-2xl font-semibold mb-2"
            style={{ color: '#ffffff' }}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            Initializing CrawlMind
          </motion.h2>
          <motion.p
            style={{ color: 'rgba(255, 255, 255, 0.7)' }}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            Setting up your AI workspace...
          </motion.p>
        </motion.div>
      </div>
    )
  }

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        delayChildren: 0.1,
        staggerChildren: 0.1
      }
    }
  }

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        type: "spring" as const,
        stiffness: 100
      }
    }
  }

  const tabVariants = {
    inactive: { scale: 0.95, opacity: 0.7 },
    active: { scale: 1, opacity: 1 }
  }

  return (
    <div className="min-h-screen" style={{ background: 'linear-gradient(135deg, #000000, #1a1a1a, #000000)' }}>
      {/* Notifications */}
      <AnimatePresence>
        {notifications.map((notification) => (
          <motion.div
            key={notification.id}
            initial={{ opacity: 0, y: -50, x: 300 }}
            animate={{ opacity: 1, y: 0, x: 0 }}
            exit={{ opacity: 0, y: -50, x: 300 }}
            className="fixed top-4 right-4 z-50 px-6 py-3 rounded-lg shadow-lg max-w-sm backdrop-blur-sm border"
            style={{
              backgroundColor: notification.type === 'success' ? 'rgba(74, 158, 255, 0.9)' :
                notification.type === 'error' ? 'rgba(74, 158, 255, 0.7)' :
                  'rgba(74, 158, 255, 0.9)',
              borderColor: 'rgba(74, 158, 255, 0.5)',
              color: '#ffffff'
            }}
          >
            {notification.message}
          </motion.div>
        ))}
      </AnimatePresence>

      <motion.div
        className="container mx-auto px-4 py-8"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        {/* Animated Header */}
        <motion.div
          className="text-center mb-12"
          variants={itemVariants}
        >
          <motion.div
            className="inline-flex items-center mb-6"
            whileHover={{ scale: 1.05 }}
            transition={{ type: "spring", stiffness: 300 }}
          >
            <div className="w-12 h-12 relative mr-4">
              <Image
                src="/artificial-intelligence.png"
                alt="CrawlMind Logo"
                width={48}
                height={48}
                className="object-contain"
              />
            </div>
            <h1
              className="text-4xl font-bold bg-clip-text text-transparent"
              style={{ background: 'linear-gradient(135deg, #4A9EFF, #87CEEB)', WebkitBackgroundClip: 'text' }}
            >
              CrawlMind AI Dashboard
            </h1>
          </motion.div>

          <motion.div
            className="flex items-center justify-center space-x-4"
            variants={itemVariants}
          >
            {user?.imageUrl && (
              <motion.img
                src={user.imageUrl}
                alt="Profile"
                className="w-16 h-16 rounded-full shadow-lg"
                style={{
                  border: '4px solid rgba(74, 158, 255, 0.5)',
                  boxShadow: '0 8px 25px rgba(74, 158, 255, 0.3)'
                }}
                whileHover={{ scale: 1.1, rotate: 5 }}
                transition={{ type: "spring", stiffness: 300 }}
              />
            )}
            <div className="text-left">
              <p className="text-2xl font-semibold" style={{ color: '#ffffff' }}>
                Welcome back, {user?.username || 'User'}! 👋
              </p>

              <p className="text-lg" style={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                Your AI-powered workspace is ready
              </p>
            </div>
          </motion.div>
        </motion.div>

        {/* Tab Navigation */}
        <motion.div
          className="max-w-4xl mx-auto mb-8"
          variants={itemVariants}
        >
          <div
            className="flex justify-center space-x-2 backdrop-blur-sm rounded-2xl p-2 shadow-lg"
            style={{
              backgroundColor: 'rgba(0, 0, 0, 0.6)',
              border: '1px solid rgba(74, 158, 255, 0.3)'
            }}
          >
            {[
              { id: 'overview', label: '📊 Overview', icon: '📊' },
              { id: 'launch', label: '🚀 Launch AI', icon: '🚀' },
              { id: 'settings', label: '⚙️ Settings', icon: '⚙️' }
            ].map((tab) => (
              <motion.button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className="flex items-center space-x-2 px-6 py-3 rounded-xl font-medium transition-all duration-200"
                style={{
                  backgroundColor: activeTab === tab.id ? '#4A9EFF' : 'transparent',
                  color: activeTab === tab.id ? '#ffffff' : 'rgba(255, 255, 255, 0.7)',
                  boxShadow: activeTab === tab.id ? '0 8px 25px rgba(74, 158, 255, 0.3)' : 'none'
                }}
                onMouseEnter={(e) => {
                  if (activeTab !== tab.id) {
                    const target = e.target as HTMLButtonElement
                    target.style.backgroundColor = 'rgba(74, 158, 255, 0.1)'
                    target.style.color = '#ffffff'
                  }
                }}
                onMouseLeave={(e) => {
                  if (activeTab !== tab.id) {
                    const target = e.target as HTMLButtonElement
                    target.style.backgroundColor = 'transparent'
                    target.style.color = 'rgba(255, 255, 255, 0.7)'
                  }
                }}
                variants={tabVariants}
                animate={activeTab === tab.id ? 'active' : 'inactive'}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <span>{tab.icon}</span>
                <span>{tab.label.split(' ')[1]}</span>
              </motion.button>
            ))}
          </div>
        </motion.div>

        {/* Main Dashboard Card */}
        <motion.div
          className="max-w-4xl mx-auto"
          variants={itemVariants}
        >
          <motion.div
            className="backdrop-blur-sm rounded-2xl shadow-2xl overflow-hidden"
            style={{
              backgroundColor: 'rgba(0, 0, 0, 0.8)',
              border: '1px solid rgba(74, 158, 255, 0.3)'
            }}
            whileHover={{ y: -5 }}
            transition={{ type: "spring", stiffness: 300 }}
          >
            {/* Dynamic Header */}
            <motion.div
              className="px-8 py-8 relative overflow-hidden"
              style={{ background: 'linear-gradient(135deg, #4A9EFF, #2d7fff, #1e5ba8)' }}
              layoutId="header"
            >
              <div
                className="absolute inset-0"
                style={{ background: 'linear-gradient(135deg, rgba(74, 158, 255, 0.2), rgba(45, 127, 255, 0.2))' }}
              ></div>
              <div className="relative z-10">
                <motion.h2
                  className="text-3xl font-bold text-white mb-2"
                  initial={{ x: -20, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  transition={{ delay: 0.2 }}
                >
                  {activeTab === 'overview' && '📊 Workspace Overview'}
                  {activeTab === 'launch' && '🚀 AI Assistant Launcher'}
                  {activeTab === 'settings' && '⚙️ Dashboard Settings'}
                </motion.h2>
                <motion.p
                  className="text-lg"
                  style={{ color: 'rgba(255, 255, 255, 0.9)' }}
                  initial={{ x: -20, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  transition={{ delay: 0.3 }}
                >
                  {activeTab === 'overview' && 'Monitor your AI workspace and authentication status'}
                  {activeTab === 'launch' && 'Access your personalized AI document analysis tools'}
                  {activeTab === 'settings' && 'Configure your dashboard preferences and integrations'}
                </motion.p>
              </div>

              {/* Animated Background Elements */}
              <motion.div
                className="absolute top-4 right-8 w-20 h-20 bg-white/10 rounded-full"
                animate={{
                  scale: [1, 1.2, 1],
                  rotate: [0, 180, 360],
                }}
                transition={{
                  duration: 8,
                  repeat: Infinity,
                  ease: "easeInOut"
                }}
              />
              <motion.div
                className="absolute bottom-4 right-16 w-12 h-12 bg-white/10 rounded-full"
                animate={{
                  scale: [1.2, 1, 1.2],
                  rotate: [360, 180, 0],
                }}
                transition={{
                  duration: 6,
                  repeat: Infinity,
                  ease: "easeInOut"
                }}
              />
            </motion.div>

            {/* Content */}
            <AnimatePresence mode="wait">
              <motion.div
                key={activeTab}
                className="p-8"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.3 }}
              >
                {/* Overview Tab */}
                {activeTab === 'overview' && (
                  <motion.div className="space-y-6" variants={containerVariants} initial="hidden" animate="visible">
                    {/* User Info Card */}
                    <motion.div
                      className="rounded-xl p-6 backdrop-blur-sm"
                      style={{
                        backgroundColor: 'rgba(0, 0, 0, 0.5)',
                        border: '1px solid rgba(74, 158, 255, 0.3)'
                      }}
                      variants={itemVariants}
                      whileHover={{ scale: 1.02 }}
                    >
                      <h3 className="text-xl font-semibold mb-4 flex items-center" style={{ color: '#ffffff' }}>
                        <div
                          className="w-8 h-8 rounded-lg flex items-center justify-center mr-3"
                          style={{ backgroundColor: '#4A9EFF' }}
                        >
                          <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" />
                          </svg>
                        </div>
                        Session Information
                      </h3>
                      <div className="grid md:grid-cols-2 gap-4">
                        {[
                          { label: 'User ID', value: userId, icon: '🆔' },
                          { label: 'Email', value: user?.primaryEmailAddress?.emailAddress, icon: '📧' },
                          { label: 'Username', value: user?.username, icon: '👤' },
                          { label: 'Status', value: 'Authenticated ✓', icon: '🔐', isStatus: true }
                        ].map((item, index) => (
                          <motion.div
                            key={item.label}
                            className="flex items-center space-x-3 p-3 rounded-lg shadow-sm"
                            style={{
                              backgroundColor: 'rgba(0, 0, 0, 0.5)',
                              border: '1px solid rgba(74, 158, 255, 0.2)'
                            }}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: index * 0.1 }}
                            whileHover={{ scale: 1.02 }}
                          >
                            <span className="text-lg">{item.icon}</span>
                            <div>
                              <p className="text-sm font-medium" style={{ color: 'rgba(255, 255, 255, 0.7)' }}>{item.label}</p>
                              <p
                                className="text-sm font-semibold"
                                style={{ color: item.isStatus ? '#4A9EFF' : '#ffffff' }}
                              >
                                {item.value}
                              </p>
                            </div>
                          </motion.div>
                        ))}
                      </div>
                    </motion.div>

                    {/* Quick Stats */}
                    <motion.div
                      className="grid md:grid-cols-3 gap-6"
                      variants={containerVariants}
                    >
                      {[
                        { title: 'AI Sessions', value: '12', change: '+3 today', icon: '🤖' },
                        { title: 'Documents Processed', value: '47', change: '+8 this week', icon: '📄' },
                        { title: 'Uptime', value: '99.9%', change: 'Last 30 days', icon: '⚡' }
                      ].map((stat, index) => (
                        <motion.div
                          key={stat.title}
                          className="rounded-xl p-6 backdrop-blur-sm"
                          style={{
                            backgroundColor: 'rgba(0, 0, 0, 0.5)',
                            border: '1px solid rgba(74, 158, 255, 0.3)'
                          }}
                          variants={itemVariants}
                          whileHover={{ scale: 1.05, rotateY: 5 }}
                          whileTap={{ scale: 0.95 }}
                        >
                          <div className="flex items-center justify-between mb-4">
                            <div
                              className="w-12 h-12 rounded-xl flex items-center justify-center text-xl"
                              style={{
                                backgroundColor: 'rgba(74, 158, 255, 0.2)',
                                border: '1px solid rgba(74, 158, 255, 0.3)',
                                color: '#4A9EFF'
                              }}
                            >
                              {stat.icon}
                            </div>
                            <span
                              className="text-2xl font-bold"
                              style={{ color: '#4A9EFF' }}
                            >
                              {stat.value}
                            </span>
                          </div>
                          <h4 className="font-semibold mb-1" style={{ color: '#ffffff' }}>{stat.title}</h4>
                          <p className="text-sm" style={{ color: 'rgba(74, 158, 255, 0.7)' }}>{stat.change}</p>
                        </motion.div>
                      ))}
                    </motion.div>
                  </motion.div>
                )}

                {/* Launch Tab */}
                {activeTab === 'launch' && (
                  <motion.div className="space-y-8" variants={containerVariants} initial="hidden" animate="visible">
                    {/* Quick Launch Section */}
                    <motion.div variants={itemVariants}>
                      <h3 className="text-2xl font-semibold text-slate-100 mb-6 flex items-center">
                        <span className="text-3xl mr-3">🚀</span>
                        AI Assistant Launcher
                      </h3>

                      <div className="grid md:grid-cols-2 gap-6">
                        {/* Option 1: Direct Launch */}
                        <motion.div
                          className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm"
                          whileHover={{ scale: 1.02, boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.3)" }}
                          variants={itemVariants}
                        >
                          <div className="flex items-center mb-4">
                            <div className="w-12 h-12 bg-orange-500/20 border border-orange-500/30 rounded-xl flex items-center justify-center mr-4">
                              <span className="text-xl text-orange-400">🔥</span>
                            </div>
                            <h4 className="text-xl font-semibold text-slate-100">Launch in New Tab</h4>
                          </div>
                          <p className="text-slate-300 mb-6">
                            Open the CrawlMind AI assistant in a new tab with seamless authentication
                          </p>
                          <div className="flex flex-wrap gap-3">
                            {streamlitUrl ? (
                              <motion.a
                                href={streamlitUrl}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="inline-flex items-center bg-orange-500 hover:bg-orange-600 text-white font-semibold py-3 px-6 rounded-xl transition-all duration-200 shadow-lg hover:shadow-xl"
                                whileHover={{ scale: 1.05 }}
                                whileTap={{ scale: 0.95 }}
                                onClick={() => addNotification('Launching AI Assistant...', 'success')}
                              >
                                <span className="mr-2">🚀</span>
                                Launch Assistant
                              </motion.a>
                            ) : (
                              <motion.button
                                onClick={() => {
                                  generateStreamlitUrl()
                                  addNotification('Preparing launch URL...', 'info')
                                }}
                                disabled={isGeneratingUrl}
                                className="inline-flex items-center bg-slate-400 text-white font-semibold py-3 px-6 rounded-xl cursor-not-allowed"
                                animate={isGeneratingUrl ? { opacity: [1, 0.5, 1] } : {}}
                                transition={{ duration: 1, repeat: isGeneratingUrl ? Infinity : 0 }}
                              >
                                <span className="mr-2">⏳</span>
                                {isGeneratingUrl ? 'Generating...' : 'Preparing...'}
                              </motion.button>
                            )}

                            <motion.button
                              onClick={() => {
                                generateStreamlitUrl()
                                addNotification('Refreshing authentication token...', 'info')
                              }}
                              disabled={isGeneratingUrl}
                              className="inline-flex items-center bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-4 rounded-xl transition-all duration-200 shadow-lg hover:shadow-xl"
                              whileHover={{ scale: 1.05 }}
                              whileTap={{ scale: 0.95 }}
                            >
                              <motion.span
                                className="mr-2"
                                animate={isGeneratingUrl ? { rotate: 360 } : {}}
                                transition={{ duration: 1, repeat: isGeneratingUrl ? Infinity : 0, ease: "linear" }}
                              >
                                🔄
                              </motion.span>
                              Refresh
                            </motion.button>
                          </div>
                        </motion.div>

                        {/* Option 2: Embedded */}
                        <motion.div
                          className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm"
                          whileHover={{ scale: 1.02, boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.3)" }}
                          variants={itemVariants}
                        >
                          <div className="flex items-center mb-4">
                            <div className="w-12 h-12 bg-purple-500/20 border border-purple-500/30 rounded-xl flex items-center justify-center mr-4">
                              <span className="text-xl text-purple-400">📱</span>
                            </div>
                            <h4 className="text-xl font-semibold text-slate-100">Embedded Assistant</h4>
                          </div>
                          <p className="text-slate-300 mb-6">
                            Use the AI assistant directly within this dashboard interface
                          </p>
                          <motion.button
                            onClick={() => {
                              setShowEmbedded(!showEmbedded)
                              addNotification(showEmbedded ? 'Hiding embedded assistant' : 'Loading embedded assistant...', 'info')
                            }}
                            className="inline-flex items-center bg-purple-500 hover:bg-purple-600 text-white font-semibold py-3 px-6 rounded-xl transition-all duration-200 shadow-lg hover:shadow-xl"
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                          >
                            <span className="mr-2">{showEmbedded ? '📴' : '📱'}</span>
                            {showEmbedded ? 'Hide Assistant' : 'Show Assistant'}
                          </motion.button>
                        </motion.div>
                      </div>
                    </motion.div>

                    {/* Embedded Frame */}
                    <AnimatePresence>
                      {showEmbedded && streamlitUrl && (
                        <motion.div
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: "600px" }}
                          exit={{ opacity: 0, height: 0 }}
                          transition={{ duration: 0.5 }}
                          className="rounded-xl overflow-hidden shadow-2xl border border-slate-700/50 backdrop-blur-sm"
                        >
                          <iframe
                            src={streamlitUrl}
                            className="w-full h-full"
                            title="CrawlMind AI Assistant"
                          />
                        </motion.div>
                      )}
                    </AnimatePresence>

                    {/* Service Status */}
                    <motion.div
                      className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm"
                      variants={itemVariants}
                      whileHover={{ scale: 1.01 }}
                    >
                      <h4 className="text-lg font-semibold text-amber-400 mb-4 flex items-center">
                        <span className="text-xl mr-2">⚡</span>
                        Service Requirements
                      </h4>
                      <p className="text-slate-300 mb-4">
                        Ensure these services are running for optimal performance:
                      </p>
                      <div className="grid md:grid-cols-3 gap-4">
                        {[
                          { name: 'Streamlit App', port: '8501', status: 'running' },
                          { name: 'FastAPI Backend', port: '8000', status: 'running' },
                          { name: 'ChromaDB', port: 'local', status: 'running' }
                        ].map((service, index) => (
                          <motion.div
                            key={service.name}
                            className="bg-slate-900/50 rounded-lg p-4 border border-slate-600/50"
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ delay: index * 0.1 }}
                          >
                            <div className="flex items-center justify-between mb-2">
                              <h5 className="font-medium text-slate-200">{service.name}</h5>
                              <span className="w-3 h-3 bg-emerald-400 rounded-full animate-pulse"></span>
                            </div>
                            <p className="text-sm text-slate-400">Port: {service.port}</p>
                          </motion.div>
                        ))}
                      </div>
                    </motion.div>
                  </motion.div>
                )}

                {/* Settings Tab */}
                {activeTab === 'settings' && (
                  <motion.div className="space-y-6" variants={containerVariants} initial="hidden" animate="visible">
                    <motion.div variants={itemVariants}>
                      <h3 className="text-2xl font-semibold text-slate-100 mb-6 flex items-center">
                        <span className="text-3xl mr-3">⚙️</span>
                        Dashboard Settings
                      </h3>

                      <div className="space-y-6">
                        {/* Theme Settings */}
                        <motion.div
                          className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 backdrop-blur-sm"
                          variants={itemVariants}
                          whileHover={{ scale: 1.01 }}
                        >
                          <h4 className="text-lg font-semibold text-slate-100 mb-4">🎨 Appearance</h4>
                          <div className="space-y-4">
                            <div className="flex items-center justify-between">
                              <span className="text-slate-300">Dark Mode</span>
                              <motion.button
                                className="w-12 h-6 bg-blue-600 rounded-full p-1 transition-colors duration-200"
                                whileTap={{ scale: 0.95 }}
                              >
                                <motion.div
                                  className="w-4 h-4 bg-white rounded-full shadow-sm translate-x-5"
                                  layout
                                />
                              </motion.button>
                            </div>
                            <div className="flex items-center justify-between">
                              <span className="text-slate-300">Reduced Motion</span>
                              <motion.button
                                className="w-12 h-6 bg-slate-600 rounded-full p-1 transition-colors duration-200"
                                whileTap={{ scale: 0.95 }}
                              >
                                <motion.div
                                  className="w-4 h-4 bg-white rounded-full shadow-sm"
                                  layout
                                />
                              </motion.button>
                            </div>
                          </div>
                        </motion.div>

                        {/* Debug Section */}
                        <motion.div
                          className="bg-slate-800/50 border border-red-500/30 rounded-xl p-6 backdrop-blur-sm"
                          variants={itemVariants}
                          whileHover={{ scale: 1.01 }}
                        >
                          <h4 className="text-lg font-semibold text-red-400 mb-4">🔧 Debug Tools</h4>
                          <motion.button
                            onClick={debugToken}
                            className="inline-flex items-center bg-red-500/20 hover:bg-red-500/30 border border-red-500/50 text-red-400 font-semibold py-3 px-6 rounded-xl transition-all duration-200 shadow-lg hover:shadow-xl"
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                          >
                            <span className="mr-2">🔍</span>
                            Debug JWT Token
                          </motion.button>
                        </motion.div>
                      </div>
                    </motion.div>
                  </motion.div>
                )}
              </motion.div>
            </AnimatePresence>
          </motion.div>
        </motion.div>

        {/* Navigation */}
        <motion.div
          className="mt-12 text-center"
          variants={itemVariants}
        >
          <Link href="/">
            <motion.button
              className="inline-flex items-center font-medium text-lg"
              style={{ color: '#4A9EFF' }}
              onMouseEnter={(e) => {
                const target = e.target as HTMLButtonElement
                target.style.color = '#87CEEB'
              }}
              onMouseLeave={(e) => {
                const target = e.target as HTMLButtonElement
                target.style.color = '#4A9EFF'
              }}
              whileHover={{ scale: 1.05, x: -5 }}
              whileTap={{ scale: 0.95 }}
            >
              <motion.span
                className="mr-2"
                animate={{ x: [-2, 0, -2] }}
                transition={{ duration: 2, repeat: Infinity }}
              >
                ←
              </motion.span>
              Back to Home
            </motion.button>
          </Link>
        </motion.div>
      </motion.div>
    </div>
  )
}