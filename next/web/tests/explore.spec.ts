import { test, expect } from '@playwright/test'
function gate() {
 let resolve!: () => void
 const promise = new Promise<void>(done => { resolve = done })
 return {promise, resolve}
}

for (const width of [1440, 390, 320]) {
 test(`explore, read, relations and history ${width}px`, async ({page}) => {
  const cards = page.locator('.concept-card')
  const searchbox = page.getByRole('textbox', {name:'搜索问题、概念或主题',exact:true})
  const service = cards.filter({has:page.getByRole('heading',{name:'服务拆分',exact:true})})
  const unrelated = cards.getByRole('heading', {name:'缓存失效',exact:true})
  async function expectSearchResults() {
   await expect(page).toHaveURL(url => new URLSearchParams(url.hash.split('?')[1]).get('q') === '拆分')
   await expect(page.getByRole('heading', {name:'搜索结果',exact:true})).toBeVisible()
   await expect(service).toHaveCount(1)
   await expect(service).toBeVisible()
   await expect(unrelated).toHaveCount(0)
  }

  await page.setViewportSize({width,height:900})
  await page.goto('/')
  await expect(page.getByRole('heading', {name:'从一个问题开始',exact:true})).toBeVisible()
  await expect(unrelated).toBeVisible()
  // Exercise the initial feature card and Chinese layout before filtering it away.
  await expect(page.getByRole('link', {name:/展开阅读/})).toBeVisible()
  await page.evaluate(() => document.fonts.ready.then(() => undefined))
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBeTruthy()
  await searchbox.fill('拆分')
  await page.getByRole('button', {name:'搜索',exact:true}).click()
  await expectSearchResults()
  await service.click()
  await expect(page.getByRole('heading', {name:'服务拆分',level:1,exact:true})).toBeVisible()
  await expect(page.locator('article')).toContainText('实际例子');
  await expect(page.locator('.relation').first()).toBeVisible();
  const original = page.url(); await page.locator('.relation').first().click();
  await expect(page).not.toHaveURL(original); await page.goBack(); await expect(page).toHaveURL(original);
  await page.goBack()
  await expectSearchResults()
  await expect(searchbox).toHaveValue('拆分')
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBeTruthy();
  await page.goForward(); await expect(page.locator('article')).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBeTruthy();
 });
}
test('empty, unavailable qualifier and direct link',async ({page})=>{
 await page.goto('/#/'); await page.getByRole('textbox').fill('zzzzzz'); await page.getByRole('button',{name:'搜索',exact:false}).click();
 await expect(page.getByText('还没有找到这个方向')).toBeVisible(); await page.getByRole('button',{name:'查看全部概念'}).click();
 await expect(page.locator('.concept-card')).toHaveCount(7); await page.locator('select').selectOption('network-planner');
 await expect(page.getByText('还没有找到这个方向')).toBeVisible();
 await page.goto('/#/concept/service-decomposition'); await expect(page.locator('article')).toContainText('边界与取舍');
 await page.goto('/#/concept/missing'); await expect(page.getByText('这个概念暂未收录。')).toBeVisible();
});
test('failure and retry are not empty state; keyboard search commits the query', async ({page}) => {
 const concepts = '**/api/v1/concepts?*'
 const cards = page.locator('.concept-card')
 const searchbox = page.getByRole('textbox')
 await page.route(concepts, route => route.abort())
 await page.goto('/')
 await expect(page.getByRole('alert')).toContainText('暂时没能打开')
 await expect(page.getByText('还没有找到这个方向')).toHaveCount(0)
 await page.unroute(concepts)
 await page.getByRole('button', {name:'重试',exact:true}).click()
 await expect(cards).toHaveCount(7)
 await expect(page.getByRole('alert')).toHaveCount(0)

 await searchbox.focus()
 await expect(searchbox).toBeFocused()
 await page.keyboard.type('ACID')
 await page.keyboard.press('Enter')
 await expect(page).toHaveURL(/#\/\?q=ACID$/)
 await expect(page.getByRole('heading', {name:'搜索结果',exact:true})).toBeVisible()
 await expect(cards).toHaveCount(1)
 await expect(cards.getByRole('heading', {name:'事务一致性',exact:true})).toBeVisible()
})

test('new navigation cancels the old search and keeps a late result out of the page', async ({page}) => {
 const slow = '**/api/v1/concepts?q=slow'
 const started = gate()
 const release = gate()
 const pageErrors: Error[] = []
 page.on('pageerror', error => pageErrors.push(error))
 await page.addInitScript(() => {
  const realFetch = window.fetch.bind(window)
  window.fetch = (input, init) => {
   if (input !== '/api/v1/concepts?q=slow') return realFetch(input, init)
   // Keep the browser request alive even after the app cancels it so the
   // stale body actually arrives. Record cancellation by the app separately.
   init?.signal?.addEventListener('abort', () => {
    document.documentElement.dataset.slowSearchCanceled = 'true'
   }, {once: true})
   return realFetch(input, {...init, signal: undefined})
  }
 })
 await page.route(slow, async route => {
  started.resolve()
  await release.promise
  await route.fulfill({json:{items:[],content_version:'stale'}})
 })
 await page.goto('/')
 await expect(page.locator('.concept-card')).toHaveCount(7)

 try {
  await page.getByRole('textbox').fill('slow')
  await page.getByRole('textbox').press('Enter')
  await started.promise
  await expect(page).toHaveURL(/q=slow$/)

  // Change only the hash, not the document containing the in-flight search.
  await page.evaluate(() => { location.hash = '/concept/service-decomposition' })
  const destination = page.getByRole('heading', {name:'服务拆分',level:1})
  await expect(destination).toBeFocused()
  await expect(page.locator('html')).toHaveAttribute('data-slow-search-canceled', 'true')
  const staleResponse = page.waitForResponse(slow)
  release.resolve()
  expect(await (await staleResponse).json()).toMatchObject({content_version:'stale'})
  // Wait for the browser to finish its render cycle after the late response.
  await page.evaluate(() => new Promise<void>(resolve =>
   requestAnimationFrame(() => requestAnimationFrame(() => resolve())),
  ))
  await expect(page).toHaveURL(/#\/concept\/service-decomposition$/)
  await expect(destination).toBeFocused()
  await expect(page.locator('article')).toContainText('实际例子')
  await expect(page.getByRole('alert')).toHaveCount(0)
  expect(pageErrors).toEqual([])
 } finally {
  release.resolve()
  await page.unrouteAll({behavior:'wait'})
 }
})

test('a keyboard user can follow a relation and reach the destination heading', async ({page}) => {
 await page.goto('/#/concept/service-decomposition')
 await expect(page.getByRole('heading', {name:'服务拆分',level:1})).toBeFocused()
 const related = page.getByRole('link', {name:/事务一致性/})
 await page.keyboard.press('Tab')
 await expect(related).toBeFocused()
 await page.keyboard.press('Enter')
 await expect(page).toHaveURL(/#\/concept\/transaction-consistency$/)
 await expect(page.getByRole('heading', {name:'事务一致性',level:1})).toBeFocused()
})

test.describe('390px touch context', () => {
 test.use({viewport:{width:390,height:900},isMobile:true,hasTouch:true})
 test('tap follows a related concept', async ({page}) => {
  await page.goto('/#/concept/service-decomposition')
  await page.getByRole('link', {name:/事务一致性/}).tap()
  await expect(page).toHaveURL(/#\/concept\/transaction-consistency$/)
  await expect(page.getByRole('heading', {name:'事务一致性',level:1})).toBeVisible()
 })
})

test('reading perspective preserves article, query, open mapping and browser history', async ({page}) => {
 await page.setViewportSize({width:390,height:900})
 await page.goto('/#/concept/quality-attribute-scenario?q=' + encodeURIComponent('质量属性') + '&qualification=architect')
 const mapping = page.locator('details.mapping')
 await mapping.locator('summary').click()
 await expect(mapping).toContainText('架构评价与度量')
 const initial = page.url()
 await page.locator('select').selectOption('systems-analyst')
 await expect(page).toHaveURL(/qualification=systems-analyst$/)
 await expect(page.locator('h1')).toHaveText('质量属性场景')
 await expect(mapping).toHaveAttribute('open', '')
 await expect(mapping).toContainText('把质量需求写成可验证场景')
 await expect(mapping).not.toContainText('架构评价与度量')
 expect(new URLSearchParams(new URL(page.url()).hash.split('?')[1]).get('q')).toBe('质量属性')
 await page.goBack()
 await expect(page).toHaveURL(initial)
 await expect(mapping).toHaveAttribute('open', '')
 await expect(mapping).toContainText('架构评价与度量')
 await page.goForward()
 await expect(mapping).toContainText('把质量需求写成可验证场景')
 await page.reload()
 await expect(page.locator('h1')).toHaveText('质量属性场景')
 await expect(page.locator('select')).toHaveValue('systems-analyst')
 await mapping.locator('summary').click()
 await expect(mapping).toContainText('把质量需求写成可验证场景')
})

test('empty filtered search can be widened without clearing keywords', async ({page}) => {
 await page.goto('/#/?q=ACID&qualification=systems-analyst')
 await expect(page.getByText('还没有找到这个方向')).toBeVisible()
 await page.getByRole('button',{name:'取消考试视角',exact:true}).click()
 await expect(page).toHaveURL(/#\/\?q=ACID$/)
 await expect(page.getByRole('textbox')).toHaveValue('ACID')
 await expect(page.getByRole('link',{name:/事务一致性/})).toBeVisible()
 await page.goBack()
 await expect(page.getByText('还没有找到这个方向')).toBeVisible()
 await expect(page.locator('select')).toHaveValue('systems-analyst')
})
