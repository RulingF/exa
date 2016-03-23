/*"""
===============
three.app.js
===============
This module provides wrappers around the `three.js`_ API for creating objects
and scenes (using the WebGL renderer). The purpose of these wrappers is to
standardize the interface to three.js when input data (such as x, y, z
coordinates) always comes from dataframe (or dataframe-like) structures. Data-
specific packages (e.g. `atomic`_) can either use the functionality provided
here or futher adapt it to suit their needs.

.. _three.js: http://threejs.org/
.. _atomic: https://github.com/exa-analytics/atomic
*/
'use strict';


require.config({
    shim: {
        'nbextensions/exa/lib/three.min': {
            exports: 'THREE'
        },

        'nbextensions/exa/lib/TrackballControls': {
            deps: ['nbextensions/exa/lib/three.min'],
            exports: 'THREE.TrackballControls'
        },

        'nbextensions/exa/marchingcubes': {
            exports: 'MarchingCubes'
        },

        'nbextensions/exa/utility': {
            exports: 'utility'
        },
    },
});


define([
    'nbextensions/exa/lib/three.min',
    'nbextensions/exa/lib/TrackballControls',
    'nbextensions/exa/marchingcubes',
    'nbextensions/exa/utility'
], function(
    THREE,
    TrackballControls,
    MarchingCubes,
    utility
) {
    var ThreeJSApp = function(canvas) {
        /*"""
        ThreeJSApp
        ==============
        A wrapper class (around the three.js functionality) used for transcribing
        Python trait data into renderable data.
        */
        this.canvas = canvas;
        this.width = this.canvas.width();
        this.height = this.canvas.height();
        this.renderer = new THREE.WebGLRenderer({
            canvas: this.canvas.get(0),
            antialias: true,
            logarithmicDepthBuffer: true,
            alpha: true,
        });
        this.renderer.setClearColor(0xFFFFFF);
        this.renderer.setSize(this.width, this.height);
        this.scene = new THREE.Scene();
        this.camera = new THREE.PerspectiveCamera(60, this.width / this.height, 0.0001, 10000);
        this.controls = new TrackballControls(this.camera, this.canvas.get(0));
        this.controls.rotateSpeed = 10.0;
        this.controls.zoomSpeed = 5.0;
        this.controls.panSpeed = 0.5;
        this.controls.noZoom = false;
        this.controls.noPan = false;
        this.controls.staticMoving = true;
        this.controls.dynamicDampingFactor = 0.3;
        this.controls.keys = [65, 83, 68];
        this.controls.addEventListener('change', this.render.bind(this));

        this.dlight1 = new THREE.DirectionalLight(0xFFFFFF, 0.4);
        this.dlight1.position.set(100, 100, 100);
        this.scene.add(this.dlight1);
        this.ambient_light = new THREE.AmbientLight(0xFFFFFF);
        this.scene.add(this.ambient_light);
    };

    ThreeJSApp.prototype.render = function() {
        /*"""
        render
        -----------
        Render the 3D application
        */
        this.renderer.render(this.scene, this.camera);
    };

    ThreeJSApp.prototype.animate = function() {
        /*"""
        animate
        ------------
        Start the animation.
        */
        window.requestAnimationFrame(this.animate.bind(this));
        this.controls.update();
    };

    ThreeJSApp.prototype.resize = function() {
        /*"""
        resize
        ------------
        Resizing of the renderer and controls
        */
        this.width = this.canvas.width();
        this.height = this.canvas.height();
        this.renderer.setSize(this.width, this.height);
        this.camera.aspect = this.width / this.height;
        this.camera.updateProjectionMatrix();
        this.controls.handleResize();
        this.render();
    };

    ThreeJSApp.prototype.add_points_from_xyz_matrix = function(values) {
        /*"""
        add_points_from_xyz_matrix
        -----------------------------
        Creates a points scene using matrix of positions.
        */
        n = values.length;
        var obj = new Float32Array(values);
        console.log(obj);
        console.log(typeof obj);
    };

    ThreeJSApp.prototype.add_spheres = function(positions, colors, radii, material) {
        /*"""
        add_sphere
        -------------
        Add spheres...?
        */
        var colors = colors || [0x9E9E9E];
        var radii = radii || [1.0];
        var material = material || THREE.MeshLambertMaterial;
        var unique_radii = utility.unique(radii);
        var unique_colors = utility.unique(colors);
        var nunique = unique_radii.length;
        var geometries = [];
        var materials = [];
        for (var i=0; i<nunique; i++) {
            geometries.push(new THREE.SphereGeometry(unique_radii[i]));
            materials.push(new material({color: unique_colors[i]}));
        };
        if (typeof positions[0] == 'object') {
            var n = positions.length;
            for (let i=0; i<n; i++) {
                var color;
                var radius;
                if (nunique == 1) {
                    color = colors[0];
                    radius = radii[0];
                } else {
                    color = colors[i];
                    radius = radii[i];
                };
                var index = unique_colors.indexOf(color);
                var mesh = new THREE.Mesh(geometries[index], materials[index]);
                mesh.position.set(positions[i][0], positions[i][1], positions[i][2]);
                this.scene.add(mesh);
            };
        } else {
            console.log('not implemented');
        };
    };

    ThreeJSApp.prototype.add_points = function(x, y, z, r, c) {
        /*"""
        add_points
        ---------------

        Args:
            x (array): x values
            y (array): y values
            z (array): z values
            r (array): radius values
            c (array): color values
        */
        var material = new THREE.ShaderMaterial({
            vertexShader: this.vertex_shader,
            fog: true,
            fragmentShader: point_frag_shader,
            transparent: false,
        })
        var geometry = new THREE.BufferGeometry();
        var color = new THREE.Color();
        var n = x.length;
        var positions = new Float32Array(n *3);
        var colors = new Float32Array(n * 3);
        var sizes = new Float32Array(n);
        for (var i=0, i3=0; i<n; i++, i3+=3) {
            positions[i3 + 0] = x[i];
            positions[i3 + 1] = y[i];
            positions[i3 + 2] = z[i];
        };
    };

    ThreeJSApp.prototype.test_mesh = function() {
        /*"""
        test_mesh
        ---------------
        Example of a render
        */
        this.test_geometry = new THREE.BoxGeometry(5, 5, 5);
        this.test_material = new THREE.MeshLambertMaterial({color: 0x005500});
        this.test_cube = new THREE.Mesh(this.test_geometry, this.test_material);
        this.scene.add(this.test_cube);
        this.camera.position.x = 20;
        this.camera.position.y = 20;
        this.camera.position.z = 20;
        this.target = new THREE.Vector3(0, 0, 0);
        this.camera.lookAt(this.target);
        this.controls.target = this.target;
        this.render();
    };

    ThreeJSApp.prototype.vertex_shader = "\
        attribute float size;\
        attribute vec3 color;\
        varying vec3 vColor;\
        \
        void main() {\
            vColor = color;\
            vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);\
            gl_PointSize = size * (450.0 / length(mvPosition.xyz));\
            gl_Position = projectionMatrix * mvPosition;\
        }\
    ";

    ThreeJSApp.prototype.point_frag_shader = "\
        varying vec3 vColor;\
        \
        void main() {\
            if (length(gl_PointCoord * 2.0 - 1.0) > 1.0)\
                discard;\
            gl_FragColor = vec4(vColor, 1.0);\
        }\
    ";

    ThreeJSApp.prototype.circle_frag_shader = "\
        varying vec3 vColor;\
        \
        void main() {\
            if (length(gl_PointCoord * 2.0 - 1.0) > 1.0)\
                discard;\
            if (length(gl_PointCoord * 2.0 - 1.0) < 0.9)\
                discard;\
            gl_FragColor = vec4(vColor, 1.0);\
        }\
    ";

    return {'ThreeJSApp': ThreeJSApp};
});
