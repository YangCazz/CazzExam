import { test, expect } from '@playwright/test'
for (const width of [1440, 390, 320]) {
 test(`explore, read, relations and history ${width}px`, async ({page}) => {
  await page.setViewportSize({width,height:900}); await page.goto('/');
  await expect(page.getByRole('heading',{name:'从一个问题开始'})).toBeVisible();
  await page.getByRole('textbox').fill('拆分'); await page.getByRole('button',{name:'搜索',exact:false}).click();
  await page.locator('.concept-card').first().click();
  await expect(page.locator('article')).toContainText('实际例子');
  await expect(page.locator('.relation').first()).toBeVisible();
  const original = page.url(); await page.locator('.relation').first().click();
  await expect(page).not.toHaveURL(original); await page.goBack(); await expect(page).toHaveURL(original);
  await page.goBack(); await expect(page.getByRole('textbox')).toHaveValue('拆分');
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
test('failure and retry are not empty state; keyboard search',async({page})=>{
 await page.route('**/api/v1/concepts?*',r=>r.abort()); await page.goto('/');
 await expect(page.getByRole('alert')).toContainText('暂时没能打开');
 await page.unroute('**/api/v1/concepts?*'); await page.getByRole('button',{name:'重试',exact:true}).click();
 await expect(page.locator('.concept-card')).toHaveCount(7);
 await page.getByRole('textbox').focus(); await page.keyboard.type('ACID'); await page.keyboard.press('Enter');
 await expect(page.locator('.concept-card')).not.toHaveCount(0);
});
test('new navigation aborts stale search',async({page})=>{
 await page.goto('/'); await expect(page.locator('.concept-card')).toHaveCount(7);
 await page.route('**/api/v1/concepts?q=slow',async r=>{await new Promise(resolve=>setTimeout(resolve,700));await r.fulfill({json:{items:[],content_version:'stale'}})});
 await page.getByRole('textbox').fill('slow'); await page.getByRole('button',{name:'搜索',exact:false}).click();
 await page.goto('/#/concept/service-decomposition'); await expect(page.locator('article')).toBeVisible();
 await page.waitForTimeout(800); await expect(page.locator('article')).toBeVisible();
});

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
