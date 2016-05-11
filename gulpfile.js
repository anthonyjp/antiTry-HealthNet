/**
 * Created by Matthew on 5/9/2016.
 */
var gulp = require('gulp'),
    sourcemaps = require('gulp-sourcemaps'),
    coffee = require('gulp-coffee'),
    coffeelint = require('gulp-coffeelint'),
    clean = require('gulp-clean'),
    gutil = require('gulp-util'),
    sass = require('gulp-sass');

var fs = require('fs');
var path = require('path');

var BASE = __dirname;
var COFFEE_IN = './static/registry/coffee/**/*.coffee';
var COFFEE_OUT = './static/compiled/registry/coffee';
var COFFEE_OUT_SRC = COFFEE_OUT + '/**/*.js';

var SASS_IN = './static/registry/css/**/*.scss';
var SASS_OUT = './static/compiled/registry/css';
var SASS_OUT_SRC_CSS = SASS_OUT + '/**/*.css';
var SASS_OUT_SRC_MAP = SASS_OUT + '/**/*.map';

gulp.task('coffee:watch', function () {
    gulp.watch(COFFEE_IN, ['clean-coffee', 'build-coffee']);
});

gulp.task('sass:watch', function () {
    gulp.watch(SASS_IN, ['clean-sass', 'build-sass']);
});

gulp.task('watch', ['coffee:watch', 'sass:watch']);

gulp.task('clean-coffee', function () {
    return gulp.src(COFFEE_OUT_SRC)
        .pipe(clean());
});

gulp.task('clean-sass', function () {
    return gulp.src([SASS_OUT_SRC_CSS, SASS_OUT_SRC_MAP])
        .pipe(clean());
});

gulp.task('clean', ['clean-coffee', 'clean-sass']);

gulp.task('lint-coffee', function () {
    return gulp.src(COFFEE_IN)
        .pipe(coffeelint('./coffeelint.json'))
        .pipe(coffeelint.reporter());
});

gulp.task('build-coffee', ['lint-coffee'], function () {
    return gulp.src(COFFEE_IN)
        .pipe(sourcemaps.init())
        .pipe(coffee({bare: true})).on('error', gutil.log)
        .pipe(sourcemaps.write())
        .pipe(gulp.dest(COFFEE_OUT));
});

gulp.task('build-sass', function () {
    return gulp.src(SASS_IN)
        .pipe(sourcemaps.init())
        .pipe(sass().on('error', sass.logError))
        .pipe(sourcemaps.write())
        .pipe(gulp.dest(SASS_OUT));
});

gulp.task('build', ['build-coffee', 'build-sass']);

gulp.task('rebuild', ['clean', 'build']);

gulp.task('default', ['rebuild']);