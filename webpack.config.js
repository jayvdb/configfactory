const path = require('path');
const CleanWebpackPlugin = require('clean-webpack-plugin');
const ManifestPlugin = require('webpack-manifest-plugin');
const MiniCssExtractPlugin = require("mini-css-extract-plugin");

module.exports = {
    mode: 'production',
    entry: {
        app: './src/configfactory/assets/app.js',
        vendor: './src/configfactory/assets/vendor.js'
    },
    plugins: [
        new CleanWebpackPlugin(['src/configfactory/static/dist']),
        new ManifestPlugin(),
        new MiniCssExtractPlugin({
            filename: "[name].css",
            chunkFilename: "[id].css"
        })
    ],
    output: {
        filename: '[name].js',
        path: path.resolve(__dirname, 'src/configfactory/static/dist')
    },
    module: {
        rules: [
            {
                test: /\.css$/,
                use: [
                    MiniCssExtractPlugin.loader,
                    "css-loader"
                ]
            },
            {
                test: /\.woff(\?v=\d+\.\d+\.\d+)?$/,
                use: {
                    loader: "url-loader",
                    options: {
                        limit: 1000,
                        mimetype: "application/font-woff"
                    }
                }
            },
            {
                test: /\.woff2(\?v=\d+\.\d+\.\d+)?$/,
                use: {
                    loader: "url-loader",
                    options: {
                        limit: 1000,
                        mimetype: "application/font-woff"
                    }
                }
            },
            {
                test: /\.ttf(\?v=\d+\.\d+\.\d+)?$/,
                use: {
                    loader: "url-loader",
                    options: {
                        limit: 1000,
                        mimetype: "application/octet-stream"
                    }
                }
            },
            {
                test: /\.eot(\?v=\d+\.\d+\.\d+)?$/,
                use: "file-loader"
            },
            {
                test: /\.svg(\?v=\d+\.\d+\.\d+)?$/,
                use: {
                    loader: "url-loader",
                    options: {
                        limit: 10000,
                        mimetype: "image/svg+xml"
                    }
                }
            }
        ]
    }
};