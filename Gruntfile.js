module.exports = function(grunt) {
    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        express: {
            all: {
                options: {
                    bases: ['./build'],
                    port: 8080,
                    hostname: "0.0.0.0",
                    livereload: true
                }
            }
        },
        open: {
            dev: {
                path: 'http://127.0.0.1:8080/',
                app: 'Google Chrome'
            }
        },
        sass: {
            dist: {
                files: {
                    'build/static/css/style.css': 'source/sass/main.scss'
                }
            }
        },
        cssmin: {
            target: {
                files: [{
                    expand: true,
                    cwd: 'build/static/css',
                    src: ['*.css', '!*.min.css'],
                    dest: 'build/static/css',
                    ext: '.min.css'
                }]
            }
        },
        copy: {
            main: {
                files: [{
                    expand: true,
                    cwd: 'source/templates/',
                    src: '**',
                    dest: 'build/',
                }, {
                    expand: true,
                    cwd: 'source/images/',
                    src: '**',
                    dest: 'build/images/',
                }, {
                    expand: true,
                    cwd: 'source/fonts/',
                    src: '**',
                    dest: 'build/static/fonts/',
                }]

            }
        },
        watch: {
            sass: {
                files: ['**/*.scss', '**/*.html'],
                tasks: ['sass', 'cssmin']
            },
            all: {
                files: '**/*.html',
                options: {
                    livereload: true
                }
            }
        }
    });

    grunt.loadNpmTasks('grunt-express');
    grunt.loadNpmTasks('grunt-open');
    grunt.loadNpmTasks('grunt-contrib-copy');
    grunt.loadNpmTasks('grunt-contrib-sass');
    grunt.loadNpmTasks('grunt-contrib-cssmin');
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.registerTask('server', ['copy', 'express', 'open', 'watch']);
    grunt.registerTask('dev', ['sass', 'cssmin', 'copy']);
}
