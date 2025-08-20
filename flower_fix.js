// Flower DataTables Ajax Error Fix
// Add this script to your Flower monitoring page to handle Ajax errors gracefully

(function() {
    'use strict';
    
    // Wait for DataTables to be ready
    $(document).ready(function() {
        
        // Fix for DataTables Ajax errors
        $.fn.dataTable.ext.errMode = 'none';
        
        // Override DataTables error handling
        if (typeof $.fn.dataTable !== 'undefined') {
            $.fn.dataTable.ext.errMode = function(settings, techNote, message) {
                console.log('DataTables error handled gracefully:', message);
                
                // Retry the Ajax request after a short delay
                setTimeout(function() {
                    if (settings && settings.oInstance) {
                        settings.oInstance.ajax.reload(null, false);
                    }
                }, 2000);
            };
        }
        
        // Handle specific workers table errors
        if ($('#workers-table').length) {
            $('#workers-table').on('error.dt', function(e, settings, techNote, message) {
                console.log('Workers table error:', message);
                
                // Show user-friendly message
                if (!$('#error-message').length) {
                    $('<div id="error-message" class="alert alert-warning" style="margin: 10px 0;">' +
                      '<strong>Connection Issue:</strong> Retrying to load worker data... ' +
                      '<button type="button" class="close" data-dismiss="alert">&times;</button>' +
                      '</div>').insertBefore('#workers-table');
                }
                
                // Auto-retry after 3 seconds
                setTimeout(function() {
                    if (settings && settings.oInstance) {
                        settings.oInstance.ajax.reload(null, false);
                        $('#error-message').fadeOut();
                    }
                }, 3000);
            });
        }
        
        // Handle page load issues
        $(window).on('load', function() {
            // If DataTables is still loading after 5 seconds, show a message
            setTimeout(function() {
                if ($('#workers-table').hasClass('dataTable') && 
                    $('#workers-table').DataTable().data().length === 0) {
                    
                    if (!$('#loading-message').length) {
                        $('<div id="loading-message" class="alert alert-info" style="margin: 10px 0;">' +
                          '<strong>Loading:</strong> Worker data is being retrieved... ' +
                          '<button type="button" class="close" data-dismiss="alert">&times;</button>' +
                          '</div>').insertBefore('#workers-table');
                    }
                }
            }, 5000);
        });
        
        // Add refresh button functionality
        if ($('.refresh-btn').length) {
            $('.refresh-btn').on('click', function(e) {
                e.preventDefault();
                
                // Clear any error messages
                $('.alert').fadeOut();
                
                // Reload all DataTables
                $('.dataTable').each(function() {
                    if ($(this).hasClass('dataTable') && $(this).DataTable()) {
                        $(this).DataTable().ajax.reload(null, false);
                    }
                });
                
                // Show success message
                $('<div class="alert alert-success" style="margin: 10px 0;">' +
                  '<strong>Refreshed:</strong> Data has been updated. ' +
                  '<button type="button" class="close" data-dismiss="alert">&times;</button>' +
                  '</div>').insertBefore('#workers-table').delay(3000).fadeOut();
            });
        }
    });
    
    // Global Ajax error handler
    $(document).ajaxError(function(event, xhr, settings, error) {
        console.log('Ajax error detected:', error);
        
        // Only handle DataTables related errors
        if (settings.url && settings.url.includes('flower')) {
            console.log('Flower Ajax error - will retry automatically');
        }
    });
    
})();
