registry.module('forms') unless registry.has('forms')

class Unit

   @registered = []

   constructor: (name, weight) ->
      @name = name
      @weight = weight
      Unit.registered.push(@)

   toString: ->
      "(#{@name}: #{@weight}"

CUSTOMARY = new Unit('customary', 'lbs')
METRIC = new Unit('metric', 'kg')

registry.forms.measurement = (($) ->
   curUnit = CUSTOMARY
   wrappers = $('.hn-measurement.wrapper')
   weightModified = no

   unitPredicate = (unit) ->
      (i, elem) -> $(elem).hasClass(unit.name)

   filterAndApply = (jObj, unit, fn) ->
      jObj.filter(unitPredicate(unit)).each(fn)

   initialize = ->
      wrappers.children().find('input').prop('required', yes)

      wrappers.children().filter(unitPredicate(METRIC)).each(->
         $(@).hide()
         $(@).find('input').prop('required', no)
      )

      wrappers.each(-> filterAndApply($(@).children(), METRIC, ->
         $(@).hide();
         $(@).find('input').prop('required', no)
      ))

   setUnit = (newUnit) ->
      wrappers.each(->
         jSelf = $(this)
         weights = jSelf.find('.weight')
         heights = jSelf.find('.height')

         return if (weights.length > 0 and not weightModified) or (heights.length > 0 and weightModified)

         children = jSelf.children()
         filterAndApply(children, curUnit, ->
            $(@).hide()
            $(@).find('input').prop('required', no)
         )

         filterAndApply(children, newUnit, ->
            $(@).show()
            $(@).find('input').prop('required', yes)
         )
      )

      $('span#weight-label').text(newUnit.weight) if weightModified

      curUnit = newUnit
      weightModified = no

   $('.hn-measurement.unit-select').change(->
      jSelf = $(@)
      weightModified = jSelf.hasClass('weight')
      setUnit(Unit.registered[jSelf.find('option:selected').first().val()], jSelf.next())
   )

   return {
      init: initialize
      setUnit: setUnit
   })(jQuery)