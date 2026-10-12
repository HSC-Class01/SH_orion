const D=window.DASHBOARD_DATA||{};
const money=v=>v==null?'—':new Intl.NumberFormat('ko-KR',{maximumFractionDigits:0}).format(v/1e6)+' 백만원';
const pct=v=>v==null?'—':Number(v).toFixed(1)+'%';
const num=v=>v==null?'—':Number(v).toFixed(2);
function latest(arr){return [...(arr||[])].sort((a,b)=>Number(b.year)-Number(a.year))[0]||{}}
const a=latest(D.annual);
document.getElementById('status').textContent=`마지막 업데이트: ${D.generated_at||'아직 수집 전'} · DART corp_code: ${D.corp_code||'미확인'} · 금액 단위: 백만원`;
document.getElementById('kpis').innerHTML=[
 ['매출액',money(a.revenue)],['영업이익',money(a.operating_income)],['영업이익률',pct(a.operating_margin)],['영업활동현금흐름',money(a.cfo)]
].map(x=>`<div class="kpi"><small>${x[0]}</small><strong>${x[1]}</strong></div>`).join('');
function chart(id,type,labels,datasets){new Chart(document.getElementById(id),{type,data:{labels,datasets},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'bottom'}},scales:{y:{ticks:{callback:v=>new Intl.NumberFormat('en',{notation:'compact'}).format(v)}}}}})}
const annual=[...(D.annual||[])].sort((x,y)=>Number(x.year)-Number(y.year));
const labels=annual.map(x=>x.year);
chart('trend','line',labels,[{label:'Revenue',data:annual.map(x=>x.revenue),tension:.25},{label:'Operating Income',data:annual.map(x=>x.operating_income),tension:.25}]);
chart('margin','line',labels,[{label:'Operating margin',data:annual.map(x=>x.operating_margin),tension:.25},{label:'Net margin',data:annual.map(x=>x.net_margin),tension:.25},{label:'ROE',data:annual.map(x=>x.roe),tension:.25}]);
chart('cashflow','bar',labels,[{label:'CFO',data:annual.map(x=>x.cfo)},{label:'CFI',data:annual.map(x=>x.cfi)},{label:'CFF',data:annual.map(x=>x.cff)},{label:'FCF',data:annual.map(x=>x.fcf)}]);
chart('structure','line',labels,[{label:'Current ratio (%)',data:annual.map(x=>x.current_ratio)},{label:'Debt ratio (%)',data:annual.map(x=>x.debt_ratio)},{label:'Equity ratio (%)',data:annual.map(x=>x.equity_ratio)}]);
const cols=[
 ['year','연도'],['report','보고서'],['revenue','매출액'],['revenue_growth','매출증가율'],['gross_profit','매출총이익'],['operating_income','영업이익'],['operating_margin','영업이익률'],['net_income','당기순이익'],['net_margin','순이익률'],['cfo','CFO'],['fcf','FCF'],['total_assets','자산총계'],['total_liabilities','부채총계'],['total_equity','자본총계'],['current_ratio','유동비율'],['quick_ratio','당좌비율'],['debt_ratio','부채비율'],['roe','ROE'],['roa','ROA'],['roic','ROIC'],['net_debt','순차입금'],['net_debt_ebitda','순차입금/EBITDA'],['interest_coverage','이자보상배율'],['dso','DSO'],['dio','DIO'],['dpo','DPO'],['ccc','CCC']
];
function makeTable(id,rows){let h='<thead><tr>'+cols.map(c=>`<th>${c[1]}</th>`).join('')+'</tr></thead><tbody>';h+=rows.sort((x,y)=>Number(y.year)-Number(x.year)).map(x=>'<tr>'+cols.map(c=>{let v=x[c[0]];if(['revenue','gross_profit','operating_income','net_income','cfo','fcf','total_assets','total_liabilities','total_equity','net_debt'].includes(c[0]))v=money(v);else if(['revenue_growth','operating_margin','net_margin','current_ratio','quick_ratio','debt_ratio','roe','roa','roic'].includes(c[0]))v=pct(v);else if(['net_debt_ebitda','interest_coverage','dso','dio','dpo','ccc'].includes(c[0]))v=num(v);return `<td>${v==null?'—':v}</td>`}).join('')+'</tr>').join('');document.getElementById(id).innerHTML=h+'</tbody>'}
makeTable('annual',D.annual||[]);makeTable('half',D.half_year||[]);makeTable('quarter',D.quarterly||[]);
document.getElementById('peers').innerHTML='<thead><tr><th>기업</th><th>종목코드</th><th>비교 포인트</th></tr></thead><tbody>'+(D.peers||[]).map(p=>`<tr><td>${p.name}</td><td>${p.ticker}</td><td>${p.focus}</td></tr>`).join('')+'</tbody>';
