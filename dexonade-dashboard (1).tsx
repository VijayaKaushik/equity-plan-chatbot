import React, { useState } from 'react';
import { CheckCircle, Clock, AlertCircle, FileText, TrendingUp, ChevronDown, ChevronUp, Edit, XCircle } from 'lucide-react';

const DexonadeDashboard = () => {
  const [expandedStage, setExpandedStage] = useState(null);
  
  // Mock data - replace with your actual data
  const [stages, setStages] = useState([
    { 
      id: 1, 
      name: 'Upload & Parsing', 
      pending: 12, 
      completed: 145,
      questions: []
    },
    { 
      id: 2, 
      name: 'Fact Extraction', 
      pending: 18, 
      completed: 132,
      questions: [
        { id: 'Q001', question: 'What is machine learning?', facts: ['ML is a subset of AI', 'Uses algorithms to learn from data'], priority: 'high' },
        { id: 'Q015', question: 'Define neural networks', facts: ['Computing systems inspired by brain', 'Composed of connected nodes'], priority: 'medium' }
      ]
    },
    { 
      id: 3, 
      name: 'Q&A Splitting', 
      pending: 15, 
      completed: 125,
      questions: []
    },
    { 
      id: 4, 
      name: 'Rewriting', 
      pending: 22, 
      completed: 118,
      questions: [
        { id: 'Q003', question: 'What is AI?', original: 'What is AI?', rewritten: 'What is artificial intelligence and how does it work?', priority: 'low' },
        { id: 'Q008', question: 'How does NLP work?', original: 'How does NLP work?', rewritten: 'How does natural language processing function in modern applications?', priority: 'high' }
      ]
    },
    { 
      id: 5, 
      name: 'Taxonomy Enhancement', 
      pending: 28, 
      completed: 95,
      questions: [
        { id: 'Q005', question: 'What are transformers?', suggestedTags: ['NLP', 'Deep Learning', 'Architecture', 'Attention Mechanism'], priority: 'medium' },
        { id: 'Q012', question: 'Explain backpropagation', suggestedTags: ['Neural Networks', 'Training', 'Optimization', 'Gradient Descent'], priority: 'high' }
      ]
    },
    { 
      id: 6, 
      name: 'Back Consolidation', 
      pending: 15, 
      completed: 82,
      questions: []
    }
  ]);

  const totalQuestions = 160;

  const handleAction = (stageId, questionId, action) => {
    setStages(prevStages => {
      return prevStages.map(stage => {
        if (stage.id === stageId) {
          return {
            ...stage,
            pending: stage.pending - 1,
            completed: action === 'approve' || action === 'modify' ? stage.completed + 1 : stage.completed,
            questions: stage.questions.filter(q => q.id !== questionId)
          };
        }
        return stage;
      });
    });
  };

  const getPriorityColor = (priority) => {
    switch(priority) {
      case 'high': return 'bg-red-100 text-red-700 border-red-300';
      case 'medium': return 'bg-yellow-100 text-yellow-700 border-yellow-300';
      case 'low': return 'bg-blue-100 text-blue-700 border-blue-300';
      default: return 'bg-gray-100 text-gray-700 border-gray-300';
    }
  };

  const renderStageReview = (stage) => {
    if (stage.name === 'Fact Extraction') {
      return (
        <div className="space-y-4">
          {stage.questions.map((item) => (
            <div key={item.id} className="border border-gray-200 rounded-lg p-4 bg-gray-50">
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <span className="font-mono text-sm text-gray-500">{item.id}</span>
                    <span className={`text-xs px-2 py-1 rounded-full border ${getPriorityColor(item.priority)}`}>
                      {item.priority.toUpperCase()}
                    </span>
                  </div>
                  <p className="text-gray-900 font-medium mb-3">{item.question}</p>
                  
                  <div className="bg-white border border-gray-200 rounded p-3">
                    <p className="text-xs font-semibold text-gray-600 mb-2">Extracted Facts:</p>
                    <ul className="space-y-1">
                      {item.facts.map((fact, idx) => (
                        <li key={idx} className="text-sm text-gray-700 flex items-start">
                          <span className="text-blue-500 mr-2">•</span>
                          <span>{fact}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
              
              <div className="flex space-x-2">
                <button 
                  onClick={() => handleAction(stage.id, item.id, 'approve')}
                  className="flex-1 px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600 transition-colors text-sm font-medium flex items-center justify-center space-x-2"
                >
                  <CheckCircle size={16} />
                  <span>Approve</span>
                </button>
                <button 
                  onClick={() => handleAction(stage.id, item.id, 'modify')}
                  className="flex-1 px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors text-sm font-medium flex items-center justify-center space-x-2"
                >
                  <Edit size={16} />
                  <span>Modify</span>
                </button>
                <button 
                  onClick={() => handleAction(stage.id, item.id, 'reject')}
                  className="flex-1 px-4 py-2 bg-red-500 text-white rounded-md hover:bg-red-600 transition-colors text-sm font-medium flex items-center justify-center space-x-2"
                >
                  <XCircle size={16} />
                  <span>Reject</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      );
    }

    if (stage.name === 'Rewriting') {
      return (
        <div className="space-y-4">
          {stage.questions.map((item) => (
            <div key={item.id} className="border border-gray-200 rounded-lg p-4 bg-gray-50">
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <span className="font-mono text-sm text-gray-500">{item.id}</span>
                    <span className={`text-xs px-2 py-1 rounded-full border ${getPriorityColor(item.priority)}`}>
                      {item.priority.toUpperCase()}
                    </span>
                  </div>
                  
                  <div className="space-y-3">
                    <div className="bg-white border border-gray-200 rounded p-3">
                      <p className="text-xs font-semibold text-gray-600 mb-1">Original:</p>
                      <p className="text-sm text-gray-700">{item.original}</p>
                    </div>
                    
                    <div className="bg-blue-50 border border-blue-200 rounded p-3">
                      <p className="text-xs font-semibold text-blue-800 mb-1">Rewritten:</p>
                      <p className="text-sm text-gray-900">{item.rewritten}</p>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="flex space-x-2">
                <button 
                  onClick={() => handleAction(stage.id, item.id, 'approve')}
                  className="flex-1 px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600 transition-colors text-sm font-medium flex items-center justify-center space-x-2"
                >
                  <CheckCircle size={16} />
                  <span>Approve</span>
                </button>
                <button 
                  onClick={() => handleAction(stage.id, item.id, 'modify')}
                  className="flex-1 px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors text-sm font-medium flex items-center justify-center space-x-2"
                >
                  <Edit size={16} />
                  <span>Modify</span>
                </button>
                <button 
                  onClick={() => handleAction(stage.id, item.id, 'reject')}
                  className="flex-1 px-4 py-2 bg-red-500 text-white rounded-md hover:bg-red-600 transition-colors text-sm font-medium flex items-center justify-center space-x-2"
                >
                  <XCircle size={16} />
                  <span>Reject</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      );
    }

    if (stage.name === 'Taxonomy Enhancement') {
      return (
        <div className="space-y-4">
          {stage.questions.map((item) => (
            <div key={item.id} className="border border-gray-200 rounded-lg p-4 bg-gray-50">
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <span className="font-mono text-sm text-gray-500">{item.id}</span>
                    <span className={`text-xs px-2 py-1 rounded-full border ${getPriorityColor(item.priority)}`}>
                      {item.priority.toUpperCase()}
                    </span>
                  </div>
                  <p className="text-gray-900 font-medium mb-3">{item.question}</p>
                  
                  <div className="bg-white border border-gray-200 rounded p-3">
                    <p className="text-xs font-semibold text-gray-600 mb-2">Suggested Taxonomy Tags:</p>
                    <div className="flex flex-wrap gap-2">
                      {item.suggestedTags.map((tag, idx) => (
                        <span key={idx} className="px-3 py-1 bg-purple-100 text-purple-700 text-sm rounded-full border border-purple-300">
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="flex space-x-2">
                <button 
                  onClick={() => handleAction(stage.id, item.id, 'approve')}
                  className="flex-1 px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600 transition-colors text-sm font-medium flex items-center justify-center space-x-2"
                >
                  <CheckCircle size={16} />
                  <span>Approve Tags</span>
                </button>
                <button 
                  onClick={() => handleAction(stage.id, item.id, 'modify')}
                  className="flex-1 px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors text-sm font-medium flex items-center justify-center space-x-2"
                >
                  <Edit size={16} />
                  <span>Edit Tags</span>
                </button>
                <button 
                  onClick={() => handleAction(stage.id, item.id, 'reject')}
                  className="flex-1 px-4 py-2 bg-red-500 text-white rounded-md hover:bg-red-600 transition-colors text-sm font-medium flex items-center justify-center space-x-2"
                >
                  <XCircle size={16} />
                  <span>Reject</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      );
    }

    return (
      <div className="text-center py-8 text-gray-500">
        No items pending review in this stage
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Dexonade Process Monitor</h1>
          <p className="text-gray-600">Real-time visibility into question processing pipeline</p>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-1 gap-4 mb-8 max-w-sm">
          <div className="bg-white rounded-lg shadow p-6 border-l-4 border-blue-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">Total Questions</p>
                <p className="text-3xl font-bold text-gray-900">{totalQuestions}</p>
              </div>
              <FileText className="text-blue-500" size={32} />
            </div>
          </div>
        </div>

        {/* Pipeline Visualization */}
        <div className="bg-white rounded-lg shadow mb-8">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">Processing Pipeline</h2>
            <p className="text-sm text-gray-600 mt-1">Click on any stage to review pending items</p>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {stages.map((stage, index) => (
                <div key={stage.id}>
                  <div 
                    className={`border rounded-lg p-4 cursor-pointer transition-all ${
                      expandedStage === stage.id ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => setExpandedStage(expandedStage === stage.id ? null : stage.id)}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4 flex-1">
                        <div className="flex-shrink-0 w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center font-semibold">
                          {stage.id}
                        </div>
                        <div className="flex-1">
                          <h3 className="font-semibold text-gray-900">{stage.name}</h3>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-6">
                        <div className="text-center">
                          <div className="flex items-center space-x-2">
                            <Clock size={16} className="text-yellow-500" />
                            <span className="text-sm font-semibold text-gray-900">{stage.pending}</span>
                          </div>
                          <p className="text-xs text-gray-500">Pending</p>
                        </div>
                        
                        <div className="text-center">
                          <div className="flex items-center space-x-2">
                            <CheckCircle size={16} className="text-green-500" />
                            <span className="text-sm font-semibold text-gray-900">{stage.completed}</span>
                          </div>
                          <p className="text-xs text-gray-500">Completed</p>
                        </div>

                        <div>
                          {expandedStage === stage.id ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                        </div>
                      </div>
                    </div>

                    {/* Progress Bar */}
                    <div className="mt-3 bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-green-500 h-2 rounded-full transition-all"
                        style={{ width: `${(stage.completed / (stage.completed + stage.pending)) * 100}%` }}
                      />
                    </div>
                  </div>

                  {/* Expanded Review Section */}
                  {expandedStage === stage.id && (
                    <div className="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
                      <h4 className="font-semibold text-gray-900 mb-4">Human Review Queue - {stage.name}</h4>
                      {renderStageReview(stage)}
                    </div>
                  )}
                  
                  {index < stages.length - 1 && (
                    <div className="flex justify-center py-2">
                      <TrendingUp className="text-gray-400" size={20} />
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DexonadeDashboard;