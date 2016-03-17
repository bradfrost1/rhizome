import { expect } from 'chai'
import ChoroplethMap from '../ChoroplethMap.js'

describe(__filename, () => {
  context('ChoroplethMap', () => {
    const choroplethMapInstance = new ChoroplethMap();
    it('should instantiate object', () => {
      expect(choroplethMapInstance).to.be.an.instanceof(ChoroplethMap);
    })
    it('should have \"defaults\" attribute', () => {
      expect(choroplethMapInstance.defaults).to.exist;
    })
    it('should have these specific defaults', () => {
      //which are needed? circle back to defaults later.
      //use .keys off of chai
      expect(choroplethMapInstance.defaults).include.keys(
        'aspect',
        'domain',
        'margin',
        'data_format', 'onClick',
        'value',
        'color',
        'xFormat',
        'name',
        'maxBubbleValue',
        'maxBubbleRadius',
        'bubbleLegendRatio',
        'indicatorName'
      );
      expect(choroplethMapInstance.defaults.margin).keys('top', 'right', 'bottom', 'left');
    })
    it('should be extensible', () => {
      expect(choroplethMapInstance).to.be.extensible;
    })
  })
})