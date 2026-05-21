(function(){
var API='';
var api=axios.create({baseURL:API,timeout:15000,withCredentials:true});
mapboxgl.accessToken='[REDACTED — Mapbox public token for account juanes2794]';

var C={conflict:'#ef4444',thermal:'#f97316',aviation:'#22d3ee',maritime:'#eab308',security:'#a855f7',oryx:'#e2e8f0',disaster:'#22c55e','mil-aviation':'#ff6b35'};
var L={conflict:'Conflicts',thermal:'FIRMS',aviation:'Civilian',maritime:'Maritime',security:'Security',oryx:'Oryx',disaster:'Disasters','mil-aviation':'Military'};

var app=Vue.createApp({
data:function(){return{
  backendStatus:'offline',currentTime:'--:--:--',
  mouseCoords:{lat:'0.0000',lng:'0.0000'},mapZoom:3,
  riskData:{},aviation:[],maritime:[],thermal:[],
  conflicts:[],oryx:[],security:[],disasters:[],
  market:{},consoleLogs:[],econ:[],infra:[],
  lossesSummary:{ru:{total:0,destroyed:0,captured:0,damaged:0},ua:{total:0,destroyed:0,captured:0,damaged:0},il:{total:0,destroyed:0,captured:0,damaged:0}},
  vl:{conflict:true,thermal:true,aviation:true,maritime:true,security:true,oryx:true,disaster:true,'mil-aviation':true},
  aiStatus:{enabled:false,callsToday:0,callsMax:6,totalTokens:0,estimatedCostUSD:'0',lastAnalysis:'',lastTime:''},
  activeTab:'intel',milAviation:[],civAviation:[],aisConnected:false
}},
computed:{
  totalFeatures:function(){return this.conflicts.length+this.thermal.length+this.aviation.length+this.maritime.length+this.security.length+this.oryx.length+this.disasters.length+this.milAviation.length}
},
mounted:function(){
  var s=this;s.log('sys','WORLDVIEW v3.4 initializing...');
  s.initMap();s.startClock();
  setTimeout(function(){s.refreshAll()},3000);
  setInterval(function(){s.refreshAll()},45000);
  setInterval(function(){s.fetchAviation()},30000);
},
methods:{
log:function(t,m){var n=new Date().toLocaleTimeString('en-US',{hour12:false});this.consoleLogs.push({type:t,text:'['+n+'] '+m});if(this.consoleLogs.length>200)this.consoleLogs.splice(0,50);var s=this;Vue.nextTick(function(){if(s.$refs.con)s.$refs.con.scrollTop=s.$refs.con.scrollHeight})},
startClock:function(){var s=this;setInterval(function(){s.currentTime=new Date().toLocaleTimeString('en-US',{hour12:false,timeZone:'UTC'})+' UTC'},1000)},
fmt:function(iso){if(!iso)return'---';try{return new Date(iso).toLocaleTimeString('en-US',{hour12:false,timeZone:'UTC'})}catch(e){return iso}},

initMap:function(){
  var s=this;
  var m=new mapboxgl.Map({container:'map',style:'mapbox://styles/mapbox/dark-v11',center:[36,38],zoom:3.5,pitch:20,antialias:true,projection:'globe'});
  m.addControl(new mapboxgl.NavigationControl(),'top-right');
  m.addControl(new mapboxgl.ScaleControl(),'bottom-right');
  m.on('style.load',function(){m.setFog({color:'rgb(5,10,30)',range:[1,10],'horizon-blend':0.08,'high-color':'rgb(20,30,60)','space-color':'rgb(5,5,15)','star-intensity':0.6})});

  m.on('load',function(){
    s.log('ok','Map loaded. Adding terrain...');
    m.addSource('mapbox-dem',{type:'raster-dem',url:'mapbox://mapbox.mapbox-terrain-dem-v1',tileSize:512});
    m.setTerrain({source:'mapbox-dem',exaggeration:1.5});

    // ALL LAYERS USE CIRCLES ONLY - no icons, no symbols, 100% reliable
    var allCats=Object.keys(C);
    allCats.forEach(function(cat){
      m.addSource(cat,{type:'geojson',data:{type:'FeatureCollection',features:[]}});

      var baseR=cat==='aviation'?3:cat==='mil-aviation'?5:cat==='maritime'?6:5;
      var glowR=baseR*3;

      // Outer glow
      m.addLayer({id:cat+'-glow',type:'circle',source:cat,paint:{
        'circle-radius':['interpolate',['linear'],['zoom'],1,glowR*0.8,5,glowR*1.2,10,glowR*2],
        'circle-color':C[cat],'circle-opacity':0.12,'circle-blur':1
      }});
      // Main dot
      m.addLayer({id:cat+'-dot',type:'circle',source:cat,paint:{
        'circle-radius':['interpolate',['linear'],['zoom'],1,baseR,5,baseR*1.5,10,baseR*3,15,baseR*5],
        'circle-color':C[cat],'circle-opacity':0.9,
        'circle-stroke-width':['interpolate',['linear'],['zoom'],1,0.5,8,2],
        'circle-stroke-color':'rgba(255,255,255,0.3)'
      }});
      // Label at zoom 5+
      m.addLayer({id:cat+'-label',type:'symbol',source:cat,minzoom:5,layout:{
        'text-field':['coalesce',['get','name'],['get','callsign'],['get','id'],['get','equipment'],['get','target'],['get','type']],
        'text-size':['interpolate',['linear'],['zoom'],5,8,10,11],
        'text-offset':[0,1.5],'text-anchor':'top',
        'text-font':['DIN Pro Medium','Arial Unicode MS Regular'],
        'text-allow-overlap':false
      },paint:{
        'text-color':C[cat],'text-halo-color':'rgba(2,6,23,0.95)','text-halo-width':1.5,
        'text-opacity':['interpolate',['linear'],['zoom'],5,0.4,8,0.85]
      }});

      // Click popup
      m.on('click',cat+'-dot',function(e){
        if(!e.features||!e.features.length)return;
        var p=e.features[0].properties;var co=e.features[0].geometry.coordinates.slice();
        new mapboxgl.Popup({offset:12,maxWidth:'320px'}).setLngLat(co).setHTML(s.popup(p,cat)).addTo(m);
      });
      m.on('mouseenter',cat+'-dot',function(){m.getCanvas().style.cursor='pointer'});
      m.on('mouseleave',cat+'-dot',function(){m.getCanvas().style.cursor=''});
    });

    s._ready=true;
    s.log('ok',allCats.length+' circle layers ready. No icons = no failures.');
  });

  m.on('mousemove',function(e){s.mouseCoords={lat:e.lngLat.lat.toFixed(4),lng:e.lngLat.lng.toFixed(4)}});
  m.on('zoomend',function(){s.mapZoom=Math.round(m.getZoom())});
  s._map=m;s._ready=false;
},

popup:function(p,cat){
  var t=p.name||p.callsign||p.id||p.equipment||p.target||p.type||'?';var c=C[cat];
  var h='<div style="font-family:monospace;font-size:11px;line-height:1.5">';
  h+='<div style="font-weight:700;color:'+c+';font-size:13px;border-bottom:1px solid '+c+'33;padding-bottom:3px;margin-bottom:3px">'+t+'</div>';
  if(p.description)h+='<div style="color:#cbd5e1">'+p.description+'</div>';
  if(p.intensity)h+='<div>Intensity: <b style="color:'+c+'">'+p.intensity+'</b></div>';
  if(p.region)h+='<div style="color:#64748b;font-size:10px">'+p.region+'</div>';
  if(p.status)h+='<div>Status: <b>'+p.status+'</b></div>';
  if(p.side)h+='<div><b style="color:'+(p.side==='RU'?'#ef4444':'#06b6d4')+'">'+p.side+'</b> '+p.equipment+' x'+p.count+'</div>';
  if(p.brightness)h+='<div>B:'+p.brightness+' C:'+(p.confidence||'?')+'%</div>';
  if(p.alt)h+='<div>ALT:'+p.alt+'m VEL:'+(p.vel||0)+'m/s HDG:'+(p.heading||0)+'</div>';
  if(p.country&&(cat==='aviation'||cat==='mil-aviation'))h+='<div style="color:#64748b">'+p.country+'</div>';
  if(p.flag)h+='<div>'+p.flag+' | '+(p.type||'')+'</div>';
  if(p.speed)h+='<div>Speed: '+Number(p.speed).toFixed(1)+'kn</div>';
  if(p.weapon)h+='<div>Weapon: <b>'+p.weapon+'</b></div>';
  if(p.impact)h+='<div style="color:#f59e0b">'+p.impact+'</div>';
  if(p.casualties)h+='<div style="color:#ef4444">'+p.casualties+'</div>';
  if(p.magnitude&&Number(p.magnitude)>0)h+='<div>Mag: <b>'+p.magnitude+'</b> Depth:'+(p.depth||'?')+'km</div>';
  if(p.date)h+='<div style="color:#334155;font-size:9px">'+p.date+'</div>';
  h+='<div style="color:#1e293b;font-size:7px;margin-top:3px;text-transform:uppercase">'+L[cat]+'</div></div>';
  return h;
},

upd:function(cat,items){
  if(!this._map||!this._ready)return;
  var src=this._map.getSource(cat);
  if(!src){this.log('err','Source '+cat+' not found');return}
  var f=items.filter(function(i){return i.lat&&i.lon&&!isNaN(i.lat)&&!isNaN(i.lon)}).map(function(i){
    return{type:'Feature',geometry:{type:'Point',coordinates:[Number(i.lon),Number(i.lat)]},properties:i};
  });
  try{src.setData({type:'FeatureCollection',features:f})}catch(e){this.log('err','setData '+cat+': '+e.message)}
},

toggleLayer:function(cat){
  this.vl[cat]=!this.vl[cat];
  var v=this.vl[cat]?'visible':'none';
  if(this._map){var m=this._map;['glow','dot','label'].forEach(function(x){var id=cat+'-'+x;if(m.getLayer(id))m.setLayoutProperty(id,'visibility',v)})}
},

refreshAll:function(){
  var s=this;s.log('sys','Refreshing...');
  s.fetchRisk();s.fetchConflicts();s.fetchThermal();s.fetchOryx();
  s.fetchMaritime();s.fetchSecurity();s.fetchDisasters();s.fetchAviation();
  s.fetchMarket();s.fetchLosses();s.fetchEcon();s.fetchInfra();s.fetchAi();
},

fetchRisk:function(){var s=this;api.get('/api/risk-summary').then(function(r){s.riskData=r.data;s.backendStatus='online';s.log('ok','Risk: '+r.data.sysStatus)}).catch(function(e){s.backendStatus='offline';s.log('err','Risk: '+(e.message||''))})},
fetchConflicts:function(){var s=this;api.get('/api/osint/conflicts').then(function(r){s.conflicts=r.data.zones||[];s.upd('conflict',s.conflicts);s.log('ok','Conflicts: '+s.conflicts.length+' ON MAP')}).catch(function(e){s.log('err','C: '+(e.message||''))})},
fetchThermal:function(){var s=this;api.get('/api/osint/thermal').then(function(r){s.thermal=r.data.hotspots||[];s.upd('thermal',s.thermal);s.log('ok','Thermal: '+s.thermal.length+' ON MAP')}).catch(function(e){s.log('err','T: '+(e.message||''))})},
fetchOryx:function(){var s=this;api.get('/api/osint/oryx').then(function(r){s.oryx=r.data.losses||[];s.upd('oryx',s.oryx);s.log('ok','Oryx: '+s.oryx.length+' ON MAP')}).catch(function(e){s.log('err','O: '+(e.message||''))})},
fetchMaritime:function(){var s=this;api.get('/api/osint/maritime').then(function(r){s.maritime=r.data.ships||[];s.aisConnected=!!r.data.aisConnected;s.upd('maritime',s.maritime);s.log('ok','Maritime: '+s.maritime.length+' '+(s.aisConnected?'AIS-LIVE':''))}).catch(function(e){s.log('err','M: '+(e.message||''))})},
fetchSecurity:function(){var s=this;api.get('/api/osint/security').then(function(r){s.security=r.data.incidents||[];s.upd('security',s.security);s.log('ok','Security: '+s.security.length+' ON MAP')}).catch(function(e){s.log('err','S: '+(e.message||''))})},
fetchDisasters:function(){var s=this;api.get('/api/osint/disasters').then(function(r){s.disasters=r.data.events||[];s.upd('disaster',s.disasters);s.log('ok','Disasters: '+s.disasters.length+' ON MAP')}).catch(function(e){s.log('err','D: '+(e.message||''))})},
fetchAviation:function(){var s=this;api.get('/api/osint/aviation').then(function(r){
  s.milAviation=r.data.military||[];s.civAviation=r.data.civilian||[];s.aviation=r.data.vectors||[];
  s.upd('aviation',s.civAviation);s.upd('mil-aviation',s.milAviation);
  s.log('ok','Aviation: '+s.aviation.length+' ('+s.milAviation.length+' mil)')
}).catch(function(e){s.log('err','A: '+(e.message||''))})},
fetchMarket:function(){var s=this;api.get('/api/portfolio').then(function(r){s.market=r.data.market||{};s.log('ok','BTC: $'+(s.market.price||'---'))}).catch(function(e){s.log('err','$: '+(e.message||''))})},
fetchLosses:function(){var s=this;api.get('/api/osint/losses').then(function(r){s.lossesSummary=r.data}).catch(function(){})},
fetchEcon:function(){var s=this;api.get('/api/osint/economic').then(function(r){s.econ=r.data.news||[]}).catch(function(){})},
fetchInfra:function(){var s=this;api.get('/api/osint/infra').then(function(r){s.infra=r.data.targets||[]}).catch(function(){})},
fetchAi:function(){var s=this;api.get('/api/ai/status').then(function(r){s.aiStatus=r.data}).catch(function(){})},

toggleAI:function(){var s=this;var n=!s.aiStatus.enabled;api.post('/api/ai/toggle',{enabled:n}).then(function(r){s.aiStatus=r.data;s.log(n?'ok':'sys','AI '+(n?'ON':'OFF'))}).catch(function(e){s.log('err','AI: '+(e.message||''))})},
runAI:function(){var s=this;s.log('sys','Running DeepSeek...');s.activeTab='ai';api.get('/api/ai/force').then(function(r){if(r.data.ok){s.log('ok','AI done. Tokens:'+r.data.tokens)}else{s.log('err','AI: '+(r.data.reason||''))}s.fetchAi()}).catch(function(e){s.log('err','AI: '+(e.message||''))})},
sendReport:function(){var s=this;s.log('sys','Sending TG...');api.get('/api/telegram/report').then(function(){s.log('ok','Report sent!')}).catch(function(e){s.log('err','TG: '+(e.message||''))})},

centerMap:function(lo,la,z){if(this._map)this._map.flyTo({center:[lo||36,la||38],zoom:z||6,pitch:20,duration:1500})},
flyToUkraine:function(){this.centerMap(36.5,48,6)},
flyToGaza:function(){this.centerMap(34.35,31.38,10)},
flyToSudan:function(){this.centerMap(32.5,15.5,6)},
flyToRedSea:function(){this.centerMap(43,14,6)},
flyToGlobal:function(){this.centerMap(10,20,2)},
flyToAmericas:function(){this.centerMap(-75,10,3.5)},
flyToColombia:function(){this.centerMap(-74,4.5,6)}
}
});
app.mount('#app');
})();
