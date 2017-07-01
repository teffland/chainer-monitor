var webpack = require("webpack");
var webpackCombineLoaders = require('webpack-combine-loaders');
var path = require("path");

var BUNDLE_DIR = path.resolve(__dirname, "src/server/static");
var SRC_DIR = path.resolve(__dirname, "src/client");
var NODE_MODULES = path.resolve(__dirname, "node_modules");

var config = {
  entry: SRC_DIR + "/index.js",
  output: {
    path: BUNDLE_DIR,
    filename: "bundle.js",
    publicPath: SRC_DIR
  },
  module: {
    loaders: [
      {
        test: /\.js?/,
        include: SRC_DIR,
        loader: "babel-loader",
        query: {
          presets: ["react", "es2015", "stage-0"]
        }
      },
      {
        test: /\.s?css$/,
        include: [ SRC_DIR ],
        loaders: [ "style-loader", "css-loader", "sass-loader"]
      }
    ]
  }
};

module.exports = config;
