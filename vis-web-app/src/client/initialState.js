/**
* Define the initial state of the app on start
*
* By doing this, you also have a an overview of the app state configuration
*/
export default {
  // auth: null,
  // tree: null,
  window: {
    width: 0,
    height: 0,
    headerHeight: 56,
    footerHeight: 56,
    headerBrand: "Chainer BS",
    headerLinks: [
      { to:'/', text:"Home" },
      { to:'/compare', text:"Compare" }
    ]
  },
  experiments: {
    fetching: false,
    fetched: false,
    fetchError: false,
    names: [],
    name2data: {}
  },
  plots: {}
}
