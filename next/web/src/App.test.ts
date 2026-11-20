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
