module.exports = function(grunt) {
  'use strict';
  // Project configuration.
  grunt.initConfig({
    pkg: '<json:package.json>',
    coffee:{
      options: {
        //bare: true
      },
      compile:{
          files:{
            'lib/*.js':  'lib/*.coffee',
            'test/*.js': 'test/*.coffee'
          }
      }
    },
    simplemocha: {
      all: {
        src: 'test/**/*.js'
      }
    },
    lint: {
      files: ['grunt.js', 'lib/**/*.js']
    },
    watch: {
      files: '<config:lint.files>',
      tasks: 'default'
    },
    jshint: {
      options: {
        curly: true,
        eqeqeq: true,
        immed: true,
        latedef: true,
        newcap: true,
        noarg: true,
        sub: true,
        undef: true,
        boss: true,
        eqnull: true,
        node: true
      },
      globals: {
        exports: true
      }
    }
  });

  grunt.loadNpmTasks('grunt-contrib-coffee');
  grunt.loadNpmTasks('grunt-simple-mocha');

  grunt.registerTask('test', 'simplemocha');
  // Default task.
  grunt.registerTask('default', 'coffee lint test');

};