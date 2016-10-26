module.exports = function(grunt) {
    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        express: {
            all: {
                options: {
                    bases: ['./source'],
                    port: 8080,
                    hostname: "0.0.0.0",
                    livereload: true
                }
            }
        },
        sass: {
            dist: {
                files: {
                  'source/static/css/style.css': 'source/sass/main.scss'
                }
            }
        },
        watch: {
            sass: {
                files: ['source/sass/**/*.scss', 'source/*.html'],
                tasks: ['sass']
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
    grunt.loadNpmTasks('grunt-contrib-sass');
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.registerTask('server', ['express', 'sass', 'watch']);
}
