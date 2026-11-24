import { mount, flushPromises } from '@vue/test-utils'
import { beforeEach, afterEach, expect, test, vi } from 'vitest'
import App from './App.vue'
const summary={id:'cx-001',slug:'service-decomposition',title:'服务拆分',summary:'理解边界',aliases:['微服务']}
const detail={...summary,content_version:'test',source_label:'原创',sections:[{heading:'实际例子',body:'例子'}],relations:[{slug:'consistency',title:'一致性',kind:'相关',reason:'跨越边界'}],mappings:[]}
let wrapper:ReturnType<typeof mount>|undefined
const fetchMock=vi.fn()
beforeEach(()=>{window.location.hash='#/';vi.stubGlobal('fetch',fetchMock);fetchMock.mockReset();fetchMock.mockImplementation(async(url:string)=>({ok:true,json:async()=>url.includes('qualifications')?{items:[{id:'architect',name:'架构师',has_content:true}],content_version:'test'}:url.includes('/concepts/')?detail:{items:[summary],content_version:'test'}}))})
afterEach(()=>{wrapper?.unmount();vi.unstubAllGlobals()})
async function navigate(hash:string){window.location.hash=hash;window.dispatchEvent(new Event('hashchange'));await flushPromises()}
test('exploration preserves search context',async()=>{wrapper=mount(App);await flushPromises();expect(wrapper.find('.concept-card').text()).toContain('服务拆分');await navigate('#/?q=微服务&qualification=architect');expect(wrapper.find('input').element.value).toBe('微服务');expect(wrapper.find('.concept-card').attributes('href')).toContain('qualification=architect')})
test('direct reading includes relation and context',async()=>{window.location.hash='#/concept/service-decomposition?q=拆分';wrapper=mount(App);await flushPromises();expect(wrapper.find('article').text()).toContain('实际例子');expect(wrapper.find('.relation').attributes('href')).toContain('q=');expect(wrapper.find('.mapping').text()).toContain('暂无已记录')})
test('error is not empty state and retries',async()=>{fetchMock.mockImplementation(async(url:string)=>{if(url.includes('qualifications'))return{ok:true,json:async()=>({items:[]})};throw new TypeError('offline')});wrapper=mount(App);await flushPromises();expect(wrapper.find('[role="alert"]').text()).toContain('暂时没能打开');expect(wrapper.text()).not.toContain('还没有找到这个方向');fetchMock.mockResolvedValue({ok:true,json:async()=>({items:[summary],content_version:'test'})});await wrapper.find('[role="alert"] button').trigger('click');await flushPromises();expect(wrapper.find('.concept-card').exists()).toBe(true)})
test('empty renders guidance',async()=>{fetchMock.mockResolvedValue({ok:true,json:async()=>({items:[],content_version:'test'})});wrapper=mount(App);await flushPromises();expect(wrapper.text()).toContain('还没有找到这个方向')})
test('map filter keeps map location',async()=>{window.location.hash='#/map';wrapper=mount(App);await flushPromises();await wrapper.find('select').setValue('architect');expect(location.hash).toBe('#/map?qualification=architect')})
test('invalid deep link does not request another API',async()=>{window.location.hash='#/concept/../qualifications';wrapper=mount(App);await flushPromises();expect(wrapper.find('[role="alert"]').text()).toContain('这个概念暂未收录');expect(fetchMock).toHaveBeenCalledTimes(1)})

test('reading lens keeps the same article, open mapping and history context', async () => {
 const architect = { qualification: 'architect', label: '架构评价与度量', evidence_status: 'editorial_topic', source_url: null }
 const analyst = { ...architect, qualification: 'systems-analyst', label: '把质量需求写成可验证场景' }
 const article = { ...detail, slug: 'quality-attribute-scenario', title: '质量属性场景', mappings: [architect, analyst] }
 fetchMock.mockImplementation(async (url: string) => ({
  ok: true, json: async () => url.endsWith('/qualifications')
   ? { items: [{ id: 'architect', name: '架构师' }, { id: 'systems-analyst', name: '系统分析师' }] }
   : article,
 }))
 const q = encodeURIComponent('质量属性')
 const initial = '#/concept/quality-attribute-scenario?q=' + q + '&qualification=architect'
 const switched = '#/concept/quality-attribute-scenario?q=' + q + '&qualification=systems-analyst'
 window.location.hash = initial
 wrapper = mount(App)
 await flushPromises()
 const originalArticle = wrapper.get('article').element
 const mapping = wrapper.get('details').element
 mapping.open = true
 expect(mapping.textContent).toContain(architect.label)
 await wrapper.get('select').setValue('systems-analyst')
 expect(location.hash).toBe(switched)
 await navigate(switched)
 expect(wrapper.get('article').element).toBe(originalArticle)
 expect(mapping.open).toBe(true)
 expect(mapping.textContent).toContain(analyst.label)
 expect(mapping.textContent).not.toContain(architect.label)
 expect(wrapper.get('.relation').attributes('href')).toContain('qualification=systems-analyst')
 await navigate(initial)
 expect(wrapper.get('select').element.value).toBe('architect')
 expect(mapping.open).toBe(true)
 expect(mapping.textContent).toContain(architect.label)
 expect(fetchMock.mock.calls.filter(([url]) => url.includes('/concepts/'))).toHaveLength(1)
})

test('clear empty-state perspective keeps committed search and discards unsent draft', async () => {
 fetchMock.mockImplementation(async (url: string) => ({
  ok: true, json: async () => url.includes('qualification=systems-analyst')
   ? { items: [] }
   : { items: [{ ...summary, title: '事务一致性' }], content_version: 'test' },
 }))
 window.location.hash = '#/?q=ACID&qualification=systems-analyst'
 wrapper = mount(App)
 await flushPromises()
 expect(wrapper.text()).toContain('还没有找到这个方向')
 await wrapper.get('input').setValue('尚未提交')
 await wrapper.get('.state button.primary').trigger('click')
 expect(location.hash).toBe('#/?q=ACID')
 await navigate('#/?q=ACID')
 expect(wrapper.get('input').element.value).toBe('ACID')
 expect(wrapper.get('.concept-card').text()).toContain('事务一致性')
 expect(wrapper.text()).not.toContain('取消考试视角')
})

test('a late response body cannot override a newly loaded article', async () => {
 const baseFetch = fetchMock.getMockImplementation()!
 let slowSignal: AbortSignal | undefined
 let settleBody!: (body: unknown) => void
 const body = new Promise<unknown>(resolve => { settleBody = resolve })
 const finishOldBody = vi.fn(() => body)
 fetchMock.mockImplementation(async (url: string, init?: RequestInit) => {
  if (url !== '/api/v1/concepts?q=slow') return baseFetch(url)
  slowSignal = init?.signal ?? undefined
  return {ok: true, json: finishOldBody}
 })

 wrapper = mount(App)
 await flushPromises()
 await navigate('#/?q=slow')
 expect(finishOldBody).toHaveBeenCalledTimes(1)
 expect(slowSignal?.aborted).toBe(false)

 await navigate('#/concept/service-decomposition')
 const article = wrapper.get('article').element
 expect(slowSignal?.aborted).toBe(true)
 expect(wrapper.get('h1').text()).toBe('服务拆分')
 settleBody({items:[],content_version:'stale'})
 await flushPromises()

 expect(wrapper.get('article').element).toBe(article)
 expect(wrapper.find('[role="alert"]').exists()).toBe(false)
 expect(wrapper.text()).not.toContain('stale')
})

test('a pending first list load does not take focus from an active search draft', async () => {
 const baseFetch = fetchMock.getMockImplementation()!
 let deliverList!: (value: unknown) => void
 const list = new Promise(resolve => { deliverList = resolve })
 fetchMock.mockImplementation((url: string) => url === '/api/v1/concepts?' ? list : baseFetch(url))

 wrapper = mount(App, {attachTo: document.body})
 const textbox = wrapper.get('input')
 textbox.element.focus()
 await textbox.setValue('拆')
 expect(document.activeElement).toBe(textbox.element)
 expect(wrapper.get('main').attributes('aria-busy')).toBe('true')
 expect(fetchMock.mock.calls.some(([url]) => url === '/api/v1/concepts?')).toBe(true)

 deliverList({ok: true, json: async () => ({items:[summary],content_version:'test'})})
 await flushPromises()

 expect(wrapper.get('.concept-card').text()).toContain('服务拆分')
 expect(wrapper.get('main').attributes('aria-busy')).toBe('false')
 expect(textbox.element.value).toBe('拆')
 expect(document.activeElement).toBe(textbox.element)

 await wrapper.get('.skip').trigger('click')
 expect(document.activeElement).toBe(wrapper.get('h1').element)
})
