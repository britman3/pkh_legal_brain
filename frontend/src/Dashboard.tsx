import React, { useState, useEffect } from 'react'

interface Rule {
  id: string
  rule_type: 'exclude_word' | 'severity_override' | 'custom_instruction'
  value: string
  severity?: 'red' | 'amber' | 'green' | 'ignore'
  instruction?: string
  enabled: boolean
}

interface RuleTypeOption {
  value: string
  label: string
  description: string
}

interface SeverityOption {
  value: string
  label: string
}

async function fetchRules(): Promise<Rule[]> {
  const res = await fetch('/api/rules/')
  if (!res.ok) throw new Error('Failed to fetch rules')
  return res.json()
}

async function fetchRuleTypes(): Promise<{ rule_types: RuleTypeOption[], severities: SeverityOption[] }> {
  const res = await fetch('/api/rules/types')
  if (!res.ok) throw new Error('Failed to fetch rule types')
  return res.json()
}

async function createRule(rule: Omit<Rule, 'id'>): Promise<Rule> {
  const res = await fetch('/api/rules/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(rule)
  })
  if (!res.ok) throw new Error('Failed to create rule')
  return res.json()
}

async function deleteRule(id: string): Promise<void> {
  const res = await fetch(`/api/rules/${id}`, { method: 'DELETE' })
  if (!res.ok) throw new Error('Failed to delete rule')
}

async function toggleRule(id: string): Promise<Rule> {
  const res = await fetch(`/api/rules/${id}/toggle`, { method: 'POST' })
  if (!res.ok) throw new Error('Failed to toggle rule')
  return res.json()
}

export default function Dashboard() {
  const [rules, setRules] = useState<Rule[]>([])
  const [ruleTypes, setRuleTypes] = useState<RuleTypeOption[]>([])
  const [severities, setSeverities] = useState<SeverityOption[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Form state
  const [newRuleType, setNewRuleType] = useState<string>('exclude_word')
  const [newValue, setNewValue] = useState('')
  const [newSeverity, setNewSeverity] = useState<string>('amber')
  const [newInstruction, setNewInstruction] = useState('')

  useEffect(() => {
    loadData()
  }, [])

  async function loadData() {
    setLoading(true)
    setError(null)
    try {
      const [rulesData, typesData] = await Promise.all([fetchRules(), fetchRuleTypes()])
      setRules(rulesData)
      setRuleTypes(typesData.rule_types)
      setSeverities(typesData.severities)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  async function handleAddRule(e: React.FormEvent) {
    e.preventDefault()
    if (!newValue.trim()) return

    try {
      const rule = await createRule({
        rule_type: newRuleType as Rule['rule_type'],
        value: newValue.trim(),
        severity: newRuleType === 'severity_override' ? newSeverity as Rule['severity'] : undefined,
        instruction: newInstruction.trim() || undefined,
        enabled: true
      })
      setRules([...rules, rule])
      setNewValue('')
      setNewInstruction('')
    } catch (err: any) {
      setError(err.message)
    }
  }

  async function handleDelete(id: string) {
    try {
      await deleteRule(id)
      setRules(rules.filter(r => r.id !== id))
    } catch (err: any) {
      setError(err.message)
    }
  }

  async function handleToggle(id: string) {
    try {
      const updated = await toggleRule(id)
      setRules(rules.map(r => r.id === id ? updated : r))
    } catch (err: any) {
      setError(err.message)
    }
  }

  function getRuleTypeLabel(type: string): string {
    const found = ruleTypes.find(t => t.value === type)
    return found?.label || type
  }

  function getSeverityLabel(sev?: string): string {
    if (!sev) return ''
    const found = severities.find(s => s.value === sev)
    return found?.label || sev
  }

  function getSeverityColor(sev?: string): string {
    switch (sev) {
      case 'red': return '#dc3545'
      case 'amber': return '#fd7e14'
      case 'green': return '#28a745'
      case 'ignore': return '#6c757d'
      default: return '#333'
    }
  }

  if (loading) return <p>Loading...</p>

  return (
    <div>
      <h2>Custom Rules Dashboard</h2>
      <p style={{ color: '#666', marginBottom: 24 }}>
        Configure rules to customise how the AI analyses and reports on legal packs.
        These rules will be applied to all future analyses.
      </p>

      {error && <p style={{ color: 'red', marginBottom: 16 }}>{error}</p>}

      {/* Add Rule Form */}
      <div style={{ background: '#f8f9fa', padding: 20, borderRadius: 8, marginBottom: 24 }}>
        <h3 style={{ marginTop: 0 }}>Add New Rule</h3>
        <form onSubmit={handleAddRule}>
          <div style={{ marginBottom: 12 }}>
            <label style={{ display: 'block', marginBottom: 4, fontWeight: 500 }}>Rule Type</label>
            <select
              value={newRuleType}
              onChange={e => setNewRuleType(e.target.value)}
              style={{ width: '100%', padding: 8, borderRadius: 4, border: '1px solid #ccc' }}
            >
              {ruleTypes.map(t => (
                <option key={t.value} value={t.value}>{t.label}</option>
              ))}
            </select>
            <small style={{ color: '#666' }}>
              {ruleTypes.find(t => t.value === newRuleType)?.description}
            </small>
          </div>

          <div style={{ marginBottom: 12 }}>
            <label style={{ display: 'block', marginBottom: 4, fontWeight: 500 }}>
              {newRuleType === 'exclude_word' ? 'Word/Phrase to Exclude' :
               newRuleType === 'severity_override' ? 'Topic/Issue' :
               'Instruction'}
            </label>
            <input
              type="text"
              value={newValue}
              onChange={e => setNewValue(e.target.value)}
              placeholder={
                newRuleType === 'exclude_word' ? 'e.g., restrictive covenant' :
                newRuleType === 'severity_override' ? 'e.g., coal mining report issues' :
                'e.g., Always highlight service charge amounts'
              }
              style={{ width: '100%', padding: 8, borderRadius: 4, border: '1px solid #ccc', boxSizing: 'border-box' }}
            />
          </div>

          {newRuleType === 'severity_override' && (
            <div style={{ marginBottom: 12 }}>
              <label style={{ display: 'block', marginBottom: 4, fontWeight: 500 }}>Severity Level</label>
              <select
                value={newSeverity}
                onChange={e => setNewSeverity(e.target.value)}
                style={{ width: '100%', padding: 8, borderRadius: 4, border: '1px solid #ccc' }}
              >
                {severities.map(s => (
                  <option key={s.value} value={s.value}>{s.label}</option>
                ))}
              </select>
            </div>
          )}

          {(newRuleType === 'severity_override' || newRuleType === 'custom_instruction') && (
            <div style={{ marginBottom: 12 }}>
              <label style={{ display: 'block', marginBottom: 4, fontWeight: 500 }}>
                Additional Notes (optional)
              </label>
              <textarea
                value={newInstruction}
                onChange={e => setNewInstruction(e.target.value)}
                placeholder="Any additional context or instructions..."
                rows={2}
                style={{ width: '100%', padding: 8, borderRadius: 4, border: '1px solid #ccc', boxSizing: 'border-box' }}
              />
            </div>
          )}

          <button
            type="submit"
            disabled={!newValue.trim()}
            style={{
              background: '#0066cc',
              color: 'white',
              border: 'none',
              padding: '10px 20px',
              borderRadius: 4,
              cursor: newValue.trim() ? 'pointer' : 'not-allowed',
              opacity: newValue.trim() ? 1 : 0.6
            }}
          >
            Add Rule
          </button>
        </form>
      </div>

      {/* Rules List */}
      <h3>Active Rules ({rules.filter(r => r.enabled).length} enabled)</h3>
      {rules.length === 0 ? (
        <p style={{ color: '#666' }}>No rules configured yet. Add your first rule above.</p>
      ) : (
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ borderBottom: '2px solid #dee2e6' }}>
              <th style={{ textAlign: 'left', padding: '12px 8px' }}>Enabled</th>
              <th style={{ textAlign: 'left', padding: '12px 8px' }}>Type</th>
              <th style={{ textAlign: 'left', padding: '12px 8px' }}>Value</th>
              <th style={{ textAlign: 'left', padding: '12px 8px' }}>Severity</th>
              <th style={{ textAlign: 'left', padding: '12px 8px' }}>Notes</th>
              <th style={{ textAlign: 'left', padding: '12px 8px' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {rules.map(rule => (
              <tr
                key={rule.id}
                style={{
                  borderBottom: '1px solid #dee2e6',
                  opacity: rule.enabled ? 1 : 0.5,
                  background: rule.enabled ? 'white' : '#f8f9fa'
                }}
              >
                <td style={{ padding: '12px 8px' }}>
                  <input
                    type="checkbox"
                    checked={rule.enabled}
                    onChange={() => handleToggle(rule.id)}
                    style={{ cursor: 'pointer', width: 18, height: 18 }}
                  />
                </td>
                <td style={{ padding: '12px 8px' }}>
                  <span style={{
                    background: '#e9ecef',
                    padding: '4px 8px',
                    borderRadius: 4,
                    fontSize: 13
                  }}>
                    {getRuleTypeLabel(rule.rule_type)}
                  </span>
                </td>
                <td style={{ padding: '12px 8px', fontWeight: 500 }}>{rule.value}</td>
                <td style={{ padding: '12px 8px' }}>
                  {rule.severity && (
                    <span style={{
                      color: 'white',
                      background: getSeverityColor(rule.severity),
                      padding: '4px 8px',
                      borderRadius: 4,
                      fontSize: 13
                    }}>
                      {getSeverityLabel(rule.severity)}
                    </span>
                  )}
                </td>
                <td style={{ padding: '12px 8px', color: '#666', fontSize: 14 }}>
                  {rule.instruction || '-'}
                </td>
                <td style={{ padding: '12px 8px' }}>
                  <button
                    onClick={() => handleDelete(rule.id)}
                    style={{
                      background: '#dc3545',
                      color: 'white',
                      border: 'none',
                      padding: '6px 12px',
                      borderRadius: 4,
                      cursor: 'pointer',
                      fontSize: 13
                    }}
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {/* Example Rules */}
      <div style={{ marginTop: 32, padding: 16, background: '#fff3cd', borderRadius: 8 }}>
        <h4 style={{ margin: '0 0 8px 0' }}>Example Rules</h4>
        <ul style={{ margin: 0, paddingLeft: 20, color: '#856404' }}>
          <li><strong>Exclude Word:</strong> "restrictive covenant" - Never mention this term in reports</li>
          <li><strong>Severity Override:</strong> "coal mining report" → Amber - Don't flag as red, just amber</li>
          <li><strong>Custom Instruction:</strong> "Always summarise ground rent escalation clauses in a separate section"</li>
        </ul>
      </div>
    </div>
  )
}
