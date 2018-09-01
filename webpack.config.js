const path = require('path');
const CleanWebpackPlugin = require('clean-webpack-plugin');
const ManifestPlugin = require('webpack-manifest-plugin');

module.exports = {
    entry: './src/configfactory/assets/js/index.js',
    plugins: [
        new CleanWebpackPlugin(['src/configfactory/static/dist']),
        new ManifestPlugin(),
    ],
    output: {
        filename: 'main.js',
        path: path.resolve(__dirname, 'src/configfactory/static/dist')
    }
};